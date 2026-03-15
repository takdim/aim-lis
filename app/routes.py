from functools import wraps

from flask import Blueprint, abort, jsonify, redirect, render_template, request, session, url_for
from datetime import datetime, timedelta

from sqlalchemy import and_, func, or_, text
from werkzeug.security import check_password_hash

from .models import (
    Biblio,
    Item,
    MstCollType,
    MstGmd,
    MstContentType,
    MstMediaType,
    MstAuthor,
    MstItemStatus,
    MstLanguage,
    MstFrequency,
    MstMemberType,
    VisitorCount,
    MstPlace,
    MstPublisher,
    MstSupplier,
    Member,
    Loan,
    Fines,
    Item,
    Biblio,
    MstLoanRules,
    MstGmd,
    BiblioView,
    SearchBiblio,
    User,
    UserGroup,
    db,
)

bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("main.login"))
        user = User.query.get(session.get("user_id"))
        if not user:
            session.pop("user_id", None)
            return redirect(url_for("main.login"))
        groups = (user.groups or "").lower()
        if groups and "admin" not in groups:
            abort(403)
        return view(*args, **kwargs)

    return wrapper


@bp.route("/login", methods=["GET", "POST"])
def login():
    message = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.passwd, password):
            message = "Username atau password salah."
        else:
            session["user_id"] = user.user_id
            return redirect(url_for("main.admin_dashboard"))

    return render_template("login.html", message=message)


@bp.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.get("/")
def opac_home():
    loan_counts = (
        db.session.query(
            Item.biblio_id,
            func.count(Loan.loan_id).label("views"),
        )
        .outerjoin(Loan, Loan.item_code == Item.item_code)
        .group_by(Item.biblio_id)
        .subquery()
    )

    def row_from(biblio, search, gmd, views):
        return {
            "biblio_id": biblio.biblio_id,
            "title": biblio.title,
            "author": search.author if search and search.author else "-",
            "year": biblio.publish_year or "-",
            "gmd": gmd.gmd_name if gmd else "Text",
            "views": int(views or 0),
        }

    latest = (
        db.session.query(Biblio, SearchBiblio, MstGmd, loan_counts.c.views)
        .outerjoin(SearchBiblio, SearchBiblio.biblio_id == Biblio.biblio_id)
        .outerjoin(MstGmd, MstGmd.gmd_id == Biblio.gmd_id)
        .outerjoin(loan_counts, loan_counts.c.biblio_id == Biblio.biblio_id)
        .order_by(Biblio.input_date.is_(None), Biblio.input_date.desc(), Biblio.biblio_id.desc())
        .limit(10)
        .all()
    )
    popular = (
        db.session.query(Biblio, SearchBiblio, MstGmd, loan_counts.c.views)
        .outerjoin(SearchBiblio, SearchBiblio.biblio_id == Biblio.biblio_id)
        .outerjoin(MstGmd, MstGmd.gmd_id == Biblio.gmd_id)
        .outerjoin(loan_counts, loan_counts.c.biblio_id == Biblio.biblio_id)
        .order_by(func.coalesce(loan_counts.c.views, 0).desc(), Biblio.biblio_id.desc())
        .limit(10)
        .all()
    )

    latest_rows = [row_from(b, s, g, v) for b, s, g, v in latest]
    popular_rows = [row_from(b, s, g, v) for b, s, g, v in popular]

    return render_template(
        "opac_home.html",
        title="OPAC",
        q="",
        search_rows=[],
        total=0,
        page=1,
        total_pages=1,
        latest_rows=latest_rows,
        popular_rows=popular_rows,
    )


@bp.route("/buku-tamu", methods=["GET", "POST"])
def guestbook_form():
    message = None
    error = None

    if request.method == "POST":
        name = (request.form.get("member_name") or "").strip()
        member_id = (request.form.get("member_id") or "").strip()
        institution = (request.form.get("institution") or "").strip()

        if not name:
            error = "Nama wajib diisi."
        else:
            member = None
            if member_id:
                member = Member.query.filter_by(member_id=member_id).first()

            if member:
                saved_name = member.member_name
                saved_inst = member.inst_name or None
                success_message = f"Selamat datang, {saved_name}."
                if saved_inst:
                    success_message = f"{success_message} Instansi: {saved_inst}."
            else:
                saved_name = name
                saved_inst = institution or None
                success_message = f"Selamat datang, {saved_name}."

            row = VisitorCount(
                member_name=saved_name,
                member_id=member_id or None,
                institution=saved_inst,
                checkin_date=datetime.utcnow(),
            )
            db.session.add(row)
            db.session.commit()
            session["guestbook_message"] = success_message
            return redirect(url_for("main.guestbook_form", success=1))

    if request.args.get("success") == "1":
        message = session.pop("guestbook_message", None) or "Terima kasih. Buku tamu berhasil disimpan."

    return render_template(
        "guestbook_form.html",
        title="Buku Tamu",
        message=message,
        error=error,
    )


@bp.post("/opac/search")
def opac_search():
    data = request.get_json(silent=True) or {}
    q = (data.get("q") or "").strip()
    page = int(data.get("page") or 1)
    if page < 1:
        page = 1
    per_page = 10

    if not q:
        return jsonify({"rows": [], "total": 0, "page": 1, "total_pages": 1})

    loan_counts = (
        db.session.query(
            Item.biblio_id,
            func.count(Loan.loan_id).label("views"),
        )
        .outerjoin(Loan, Loan.item_code == Item.item_code)
        .group_by(Item.biblio_id)
        .subquery()
    )

    like = f"%{q}%"
    base = (
        db.session.query(Biblio)
        .outerjoin(SearchBiblio, SearchBiblio.biblio_id == Biblio.biblio_id)
        .filter(
            or_(
                Biblio.title.ilike(like),
                Biblio.isbn_issn.ilike(like),
                Biblio.call_number.ilike(like),
                SearchBiblio.author.ilike(like),
                SearchBiblio.topic.ilike(like),
            )
        )
    )
    total = base.with_entities(func.count(Biblio.biblio_id)).scalar() or 0
    total_pages = max((total + per_page - 1) // per_page, 1)
    if page > total_pages:
        page = total_pages

    results = (
        db.session.query(Biblio, SearchBiblio, MstGmd, loan_counts.c.views)
        .outerjoin(SearchBiblio, SearchBiblio.biblio_id == Biblio.biblio_id)
        .outerjoin(MstGmd, MstGmd.gmd_id == Biblio.gmd_id)
        .outerjoin(loan_counts, loan_counts.c.biblio_id == Biblio.biblio_id)
        .filter(
            or_(
                Biblio.title.ilike(like),
                Biblio.isbn_issn.ilike(like),
                Biblio.call_number.ilike(like),
                SearchBiblio.author.ilike(like),
                SearchBiblio.topic.ilike(like),
            )
        )
        .order_by(Biblio.title.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    rows = []
    for b, s, g, v in results:
        rows.append(
            {
                "biblio_id": b.biblio_id,
                "title": b.title,
                "author": s.author if s and s.author else "-",
                "year": b.publish_year or "-",
                "gmd": g.gmd_name if g else "Text",
                "views": int(v or 0),
            }
        )

    return jsonify({"rows": rows, "total": total, "page": page, "total_pages": total_pages, "q": q})


@bp.get("/admin")
@login_required
def admin_dashboard():
    return render_template(
        "admin/dashboard.html",
        title="Dashboard",
        crumbs="Dashboard",
        active="dashboard",
    )


@bp.get("/admin/bibliografi")
@login_required
def admin_biblio():
    per_page = 10
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    q = request.args.get("q", "").strip()

    base_query = db.session.query(Biblio).outerjoin(
        SearchBiblio, SearchBiblio.biblio_id == Biblio.biblio_id
    )
    if q:
        like = f"%{q}%"
        base_query = base_query.filter(
            or_(
                Biblio.title.ilike(like),
                Biblio.isbn_issn.ilike(like),
                Biblio.call_number.ilike(like),
                SearchBiblio.author.ilike(like),
                SearchBiblio.topic.ilike(like),
            )
        )

    total_count = base_query.with_entities(func.count(Biblio.biblio_id)).scalar() or 0
    total_pages = max((total_count + per_page - 1) // per_page, 1)
    if page > total_pages:
        page = total_pages

    item_counts = (
        db.session.query(
            Item.biblio_id,
            func.count(Item.item_id).label("copies"),
        )
        .group_by(Item.biblio_id)
        .subquery()
    )

    query = (
        db.session.query(Biblio, SearchBiblio, item_counts.c.copies)
        .outerjoin(SearchBiblio, SearchBiblio.biblio_id == Biblio.biblio_id)
        .outerjoin(item_counts, item_counts.c.biblio_id == Biblio.biblio_id)
    )
    if q:
        query = query.filter(
            or_(
                Biblio.title.ilike(like),
                Biblio.isbn_issn.ilike(like),
                Biblio.call_number.ilike(like),
                SearchBiblio.author.ilike(like),
                SearchBiblio.topic.ilike(like),
            )
        )

    query = (
        query.order_by(Biblio.biblio_id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    rows = []
    for biblio, search_biblio, copies in query:
        author = (
            search_biblio.author.strip()
            if search_biblio and search_biblio.author
            else "Tanpa penulis"
        )
        year = biblio.publish_year or "-"
        updated = biblio.last_update.strftime("%d/%m/%Y") if biblio.last_update else "-"

        rows.append(
            {
                "id": biblio.biblio_id,
                "title": biblio.title,
                "meta": f"{author} · {year}",
                "isbn": biblio.isbn_issn or "-",
                "copies": copies or 0,
                "updated": updated,
            }
        )

    if request.args.get("format") == "json":
        return jsonify(
            {
                "rows": rows,
                "total_count": total_count,
                "page": page,
                "total_pages": total_pages,
                "q": q,
            }
        )

    return render_template(
        "admin/biblio_list.html",
        title="Daftar Bibliografi",
        crumbs="Daftar Bibliografi",
        active="biblio",
        rows=rows,
        total_count=total_count,
        page=page,
        total_pages=total_pages,
        q=q,
    )


@bp.get("/admin/eksemplar")
@login_required
def admin_items():
    per_page = 10
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    q = request.args.get("q", "").strip()

    base_query = db.session.query(Item).outerjoin(Biblio, Biblio.biblio_id == Item.biblio_id)
    if q:
        like = f"%{q}%"
        base_query = base_query.filter(
            or_(
                Item.item_code.ilike(like),
                Item.inventory_code.ilike(like),
                Item.call_number.ilike(like),
                Biblio.title.ilike(like),
            )
        )

    total_count = base_query.with_entities(func.count(Item.item_id)).scalar() or 0
    total_pages = max((total_count + per_page - 1) // per_page, 1)
    if page > total_pages:
        page = total_pages

    query = (
        db.session.query(Item, Biblio, MstCollType)
        .outerjoin(Biblio, Biblio.biblio_id == Item.biblio_id)
        .outerjoin(MstCollType, MstCollType.coll_type_id == Item.coll_type_id)
    )
    if q:
        query = query.filter(
            or_(
                Item.item_code.ilike(like),
                Item.inventory_code.ilike(like),
                Item.call_number.ilike(like),
                Biblio.title.ilike(like),
            )
        )

    query = (
        query.order_by(Item.item_id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    rows = []
    for item, biblio, coll_type in query:
        updated = item.last_update.strftime("%d/%m/%Y %H:%M") if item.last_update else "-"
        code = item.item_code or item.inventory_code or "-"
        rows.append(
            {
                "id": item.item_id,
                "code": code,
                "title": biblio.title if biblio else "-",
                "coll_type": coll_type.coll_type_name if coll_type else "-",
                "location": item.location_id or "-",
                "call_number": item.call_number or "-",
                "updated": updated,
                "inventory_code": item.inventory_code or item.item_code or "",
                "location_id": item.location_id or "",
                "site": item.site or "",
                "coll_type_id": item.coll_type_id or "",
                "item_status_id": item.item_status_id or "",
                "order_no": item.order_no or "",
                "received_date": item.received_date.strftime("%Y-%m-%d") if item.received_date else "",
                "supplier_id": item.supplier_id or "",
                "source": item.source or 0,
                "invoice": item.invoice or "",
                "invoice_date": item.invoice_date.strftime("%Y-%m-%d") if item.invoice_date else "",
                "price": item.price or "",
            }
        )

    if request.args.get("format") == "json":
        return jsonify(
            {
                "rows": rows,
                "total_count": total_count,
                "page": page,
                "total_pages": total_pages,
                "q": q,
            }
        )

    coll_types = MstCollType.query.order_by(MstCollType.coll_type_name.asc()).all()
    item_statuses = MstItemStatus.query.order_by(MstItemStatus.item_status_name.asc()).all()
    suppliers = MstSupplier.query.order_by(MstSupplier.supplier_name.asc()).all()

    return render_template(
        "admin/item_list.html",
        title="Daftar Eksemplar",
        crumbs="Daftar Eksemplar",
        active="items",
        rows=rows,
        coll_types=coll_types,
        item_statuses=item_statuses,
        suppliers=suppliers,
        total_count=total_count,
        page=page,
        total_pages=total_pages,
        q=q,
    )


@bp.post("/admin/items/delete")
@login_required
def admin_items_delete():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []
    if not isinstance(ids, list) or not ids:
        return jsonify({"ok": False, "error": "ID tidak valid."}), 400

    (
        db.session.query(Item)
        .filter(Item.item_id.in_(ids))
        .delete(synchronize_session=False)
    )
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/admin/label-barcode")
@login_required
def admin_labels():
    per_page = 10
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    q = request.args.get("q", "").strip()

    base_query = db.session.query(Item).outerjoin(Biblio, Biblio.biblio_id == Item.biblio_id)
    if q:
        like = f"%{q}%"
        base_query = base_query.filter(
            or_(
                Item.item_code.ilike(like),
                Item.inventory_code.ilike(like),
                Item.call_number.ilike(like),
                Biblio.title.ilike(like),
            )
        )

    total_count = base_query.with_entities(func.count(Item.item_id)).scalar() or 0
    total_pages = max((total_count + per_page - 1) // per_page, 1)
    if page > total_pages:
        page = total_pages

    query = db.session.query(Item, Biblio).outerjoin(Biblio, Biblio.biblio_id == Item.biblio_id)
    if q:
        query = query.filter(
            or_(
                Item.item_code.ilike(like),
                Item.inventory_code.ilike(like),
                Item.call_number.ilike(like),
                Biblio.title.ilike(like),
            )
        )

    query = (
        query.order_by(Item.item_id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    rows = []
    for item, biblio in query:
        code = item.item_code or item.inventory_code or "-"
        rows.append(
            {
                "id": item.item_id,
                "code": code,
                "title": biblio.title if biblio else "-",
                "call_number": item.call_number or "-",
            }
        )

    if request.args.get("format") == "json":
        return jsonify(
            {
                "rows": rows,
                "total_count": total_count,
                "page": page,
                "total_pages": total_pages,
                "q": q,
            }
        )

    return render_template(
        "admin/label_print.html",
        title="Cetak Label & Barcode",
        crumbs="Cetak Label & Barcode",
        active="labels",
        rows=rows,
        total_count=total_count,
        page=page,
        total_pages=total_pages,
        q=q,
    )


@bp.route("/admin/tipe-keanggotaan", methods=["GET", "POST"])
@login_required
def admin_member_types():
    if request.method == "POST":
        name = (request.form.get("member_type_name") or "").strip()
        if name:
            member_type = MstMemberType(
                member_type_name=name,
                loan_limit=int(request.form.get("loan_limit") or 0),
                loan_periode=int(request.form.get("loan_periode") or 0),
                member_periode=int(request.form.get("member_periode") or 0),
                fine_each_day=int(request.form.get("fine_each_day") or 0),
                input_date=datetime.utcnow().date(),
                last_update=datetime.utcnow().date(),
            )
            db.session.add(member_type)
            db.session.commit()
        return redirect(url_for("main.admin_member_types"))

    types = MstMemberType.query.order_by(MstMemberType.member_type_name.asc()).all()
    rows = []
    for t in types:
        rows.append(
            {
                "member_type_id": t.member_type_id,
                "member_type_name": t.member_type_name,
                "loan_limit": t.loan_limit,
                "loan_periode": t.loan_periode,
                "loan_extend": t.reborrow_limit or 0,
                "fine_each_day": t.fine_each_day,
                "reserve_limit": t.reserve_limit or 0,
            }
        )

    return render_template(
        "admin/member_type.html",
        title="Tipe Keanggotaan",
        crumbs="Tipe Keanggotaan",
        active="member_type",
        rows=rows,
    )


@bp.post("/admin/tipe-keanggotaan/<int:member_type_id>/update")
@login_required
def admin_member_type_update(member_type_id: int):
    member_type = MstMemberType.query.get_or_404(member_type_id)
    data = request.get_json(silent=True) or {}
    name = (data.get("member_type_name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "Nama tipe wajib diisi."}), 400

    member_type.member_type_name = name
    member_type.loan_limit = int(data.get("loan_limit") or 0)
    member_type.loan_periode = int(data.get("loan_periode") or 0)
    member_type.member_periode = int(data.get("member_periode") or 0)
    member_type.fine_each_day = int(data.get("fine_each_day") or 0)
    member_type.last_update = datetime.utcnow().date()
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/tipe-keanggotaan/<int:member_type_id>/delete")
@login_required
def admin_member_type_delete(member_type_id: int):
    member_type = MstMemberType.query.get_or_404(member_type_id)
    db.session.delete(member_type)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/admin/anggota")
@login_required
def admin_members():
    per_page = 10
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    q = request.args.get("q", "").strip()

    base_query = db.session.query(Member).outerjoin(
        MstMemberType, MstMemberType.member_type_id == Member.member_type_id
    )
    if q:
        like = f"%{q}%"
        base_query = base_query.filter(
            or_(Member.member_name.ilike(like), Member.member_id.ilike(like))
        )

    total_count = base_query.with_entities(func.count(Member.member_id)).scalar() or 0
    total_pages = max((total_count + per_page - 1) // per_page, 1)
    if page > total_pages:
        page = total_pages

    query = db.session.query(Member, MstMemberType).outerjoin(
        MstMemberType, MstMemberType.member_type_id == Member.member_type_id
    )
    if q:
        query = query.filter(
            or_(Member.member_name.ilike(like), Member.member_id.ilike(like))
        )

    query = (
        query.order_by(Member.member_name.asc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )

    rows = []
    for member, mtype in query:
        expire_display = (
            member.expire_date.strftime("%d %b %Y")
            if member.expire_date
            else "-"
        )
        status = "inactive" if member.is_pending else "active"
        rows.append(
            {
                "member_id": member.member_id,
                "member_name": member.member_name,
                "member_type_id": member.member_type_id or "",
                "member_type_name": mtype.member_type_name if mtype else "-",
                "expire_date": member.expire_date.strftime("%Y-%m-%d")
                if member.expire_date
                else "",
                "expire_date_display": expire_display,
                "inst_name": member.inst_name or "-",
                "status": status,
            }
        )

    if request.args.get("format") == "json":
        return jsonify(
            {
                "rows": rows,
                "total_count": total_count,
                "page": page,
                "total_pages": total_pages,
                "q": q,
            }
        )

    member_types = MstMemberType.query.order_by(MstMemberType.member_type_name.asc()).all()
    return render_template(
        "admin/member_list.html",
        title="Daftar Anggota",
        crumbs="Daftar Anggota",
        active="members",
        rows=rows,
        member_types=member_types,
        total_count=total_count,
        page=page,
        total_pages=total_pages,
        q=q,
    )


@bp.get("/admin/buku-tamu")
@login_required
def admin_guestbook():
    per_page = 10
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    q = request.args.get("q", "").strip()

    base_query = db.session.query(VisitorCount)
    if q:
        like = f"%{q}%"
        base_query = base_query.filter(
            or_(
                VisitorCount.member_name.ilike(like),
                VisitorCount.member_id.ilike(like),
                VisitorCount.institution.ilike(like),
            )
        )

    total_count = base_query.with_entities(func.count(VisitorCount.visitor_id)).scalar() or 0
    total_pages = max((total_count + per_page - 1) // per_page, 1)
    if page > total_pages:
        page = total_pages

    query = base_query.order_by(
        VisitorCount.checkin_date.desc(),
        VisitorCount.visitor_id.desc(),
    )
    query = query.offset((page - 1) * per_page).limit(per_page)

    rows = []
    for row in query:
        checkin = (
            row.checkin_date.strftime("%d %b %Y %H:%M")
            if row.checkin_date
            else "-"
        )
        rows.append(
            {
                "checkin_date": checkin,
                "member_name": row.member_name or "-",
                "member_id": row.member_id or "-",
                "institution": row.institution or "-",
            }
        )

    return render_template(
        "admin/guestbook.html",
        title="Buku Tamu",
        crumbs="Buku Tamu",
        active="guestbook",
        rows=rows,
        q=q,
        page=page,
        total_pages=total_pages,
        total_count=total_count,
    )


@bp.get("/admin/masterfile/gmd")
@login_required
def admin_master_gmd():
    rows = MstGmd.query.order_by(MstGmd.gmd_name.asc()).all()
    return render_template(
        "admin/master_gmd.html",
        title="Master GMD",
        crumbs="Masterfile / GMD",
        active="master_gmd",
        rows=rows,
    )


@bp.post("/admin/masterfile/gmd/create")
@login_required
def admin_master_gmd_create():
    name = (request.form.get("gmd_name") or "").strip()
    if not name:
        return redirect(url_for("main.admin_master_gmd"))
    gmd = MstGmd(
        gmd_code=(request.form.get("gmd_code") or "").strip() or None,
        gmd_name=name,
        icon_image=(request.form.get("icon_image") or "").strip() or None,
        input_date=datetime.utcnow().date(),
        last_update=datetime.utcnow().date(),
    )
    db.session.add(gmd)
    db.session.commit()
    return redirect(url_for("main.admin_master_gmd"))


@bp.post("/admin/masterfile/gmd/<int:gmd_id>/update")
@login_required
def admin_master_gmd_update(gmd_id: int):
    gmd = MstGmd.query.get_or_404(gmd_id)
    data = request.get_json(silent=True) or {}
    name = (data.get("gmd_name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "Nama GMD wajib diisi."}), 400
    gmd.gmd_name = name
    gmd.gmd_code = (data.get("gmd_code") or "").strip() or None
    gmd.icon_image = (data.get("icon_image") or "").strip() or None
    gmd.last_update = datetime.utcnow().date()
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/masterfile/gmd/<int:gmd_id>/delete")
@login_required
def admin_master_gmd_delete(gmd_id: int):
    gmd = MstGmd.query.get_or_404(gmd_id)
    db.session.delete(gmd)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/admin/masterfile/tipe-isi")
@login_required
def admin_master_content_type():
    rows = MstContentType.query.order_by(MstContentType.content_type.asc()).all()
    return render_template(
        "admin/master_content_type.html",
        title="Master Tipe Isi",
        crumbs="Masterfile / Tipe Isi",
        active="master_content",
        rows=rows,
    )


@bp.post("/admin/masterfile/tipe-isi/create")
@login_required
def admin_master_content_type_create():
    name = (request.form.get("content_type") or "").strip()
    code = (request.form.get("code") or "").strip()
    code2 = (request.form.get("code2") or "").strip()
    if not name or not code or not code2:
        return redirect(url_for("main.admin_master_content_type"))
    row = MstContentType(
        content_type=name,
        code=code,
        code2=code2,
        input_date=datetime.utcnow(),
        last_update=datetime.utcnow(),
    )
    db.session.add(row)
    db.session.commit()
    return redirect(url_for("main.admin_master_content_type"))


@bp.post("/admin/masterfile/tipe-isi/<int:row_id>/update")
@login_required
def admin_master_content_type_update(row_id: int):
    row = MstContentType.query.get_or_404(row_id)
    data = request.get_json(silent=True) or {}
    name = (data.get("content_type") or "").strip()
    code = (data.get("code") or "").strip()
    code2 = (data.get("code2") or "").strip()
    if not name or not code or not code2:
        return jsonify({"ok": False, "error": "Semua field wajib diisi."}), 400
    row.content_type = name
    row.code = code
    row.code2 = code2
    row.last_update = datetime.utcnow()
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/masterfile/tipe-isi/<int:row_id>/delete")
@login_required
def admin_master_content_type_delete(row_id: int):
    row = MstContentType.query.get_or_404(row_id)
    db.session.delete(row)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/admin/masterfile/tipe-media")
@login_required
def admin_master_media_type():
    rows = MstMediaType.query.order_by(MstMediaType.media_type.asc()).all()
    return render_template(
        "admin/master_media_type.html",
        title="Master Tipe Media",
        crumbs="Masterfile / Tipe Media",
        active="master_media",
        rows=rows,
    )


@bp.post("/admin/masterfile/tipe-media/create")
@login_required
def admin_master_media_type_create():
    name = (request.form.get("media_type") or "").strip()
    code = (request.form.get("code") or "").strip()
    code2 = (request.form.get("code2") or "").strip()
    if not name or not code or not code2:
        return redirect(url_for("main.admin_master_media_type"))
    row = MstMediaType(
        media_type=name,
        code=code,
        code2=code2,
        input_date=datetime.utcnow(),
        last_update=datetime.utcnow(),
    )
    db.session.add(row)
    db.session.commit()
    return redirect(url_for("main.admin_master_media_type"))


@bp.post("/admin/masterfile/tipe-media/<int:row_id>/update")
@login_required
def admin_master_media_type_update(row_id: int):
    row = MstMediaType.query.get_or_404(row_id)
    data = request.get_json(silent=True) or {}
    name = (data.get("media_type") or "").strip()
    code = (data.get("code") or "").strip()
    code2 = (data.get("code2") or "").strip()
    if not name or not code or not code2:
        return jsonify({"ok": False, "error": "Semua field wajib diisi."}), 400
    row.media_type = name
    row.code = code
    row.code2 = code2
    row.last_update = datetime.utcnow()
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/masterfile/tipe-media/<int:row_id>/delete")
@login_required
def admin_master_media_type_delete(row_id: int):
    row = MstMediaType.query.get_or_404(row_id)
    db.session.delete(row)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/admin/masterfile/pengarang")
@login_required
def admin_master_author():
    rows = MstAuthor.query.order_by(MstAuthor.author_name.asc()).all()
    return render_template(
        "admin/master_author.html",
        title="Master Pengarang",
        crumbs="Masterfile / Pengarang",
        active="master_author",
        rows=rows,
    )


@bp.post("/admin/masterfile/pengarang/create")
@login_required
def admin_master_author_create():
    name = (request.form.get("author_name") or "").strip()
    if not name:
        return redirect(url_for("main.admin_master_author"))
    row = MstAuthor(
        author_name=name,
        author_year=(request.form.get("author_year") or "").strip() or None,
        authority_type=(request.form.get("authority_type") or "").strip() or "p",
        auth_list=None,
        input_date=datetime.utcnow().date(),
        last_update=datetime.utcnow().date(),
    )
    db.session.add(row)
    db.session.commit()
    return redirect(url_for("main.admin_master_author"))


@bp.post("/admin/masterfile/pengarang/<int:row_id>/update")
@login_required
def admin_master_author_update(row_id: int):
    row = MstAuthor.query.get_or_404(row_id)
    data = request.get_json(silent=True) or {}
    name = (data.get("author_name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "Nama pengarang wajib diisi."}), 400
    row.author_name = name
    row.author_year = (data.get("author_year") or "").strip() or None
    row.authority_type = (data.get("authority_type") or "").strip() or "p"
    row.last_update = datetime.utcnow().date()
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/masterfile/pengarang/<int:row_id>/delete")
@login_required
def admin_master_author_delete(row_id: int):
    row = MstAuthor.query.get_or_404(row_id)
    db.session.delete(row)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/admin/masterfile/penerbit")
@login_required
def admin_master_publisher():
    rows = MstPublisher.query.order_by(MstPublisher.publisher_name.asc()).all()
    return render_template(
        "admin/master_publisher.html",
        title="Master Penerbit",
        crumbs="Masterfile / Penerbit",
        active="master_publisher",
        rows=rows,
    )


@bp.post("/admin/masterfile/penerbit/create")
@login_required
def admin_master_publisher_create():
    name = (request.form.get("publisher_name") or "").strip()
    if not name:
        return redirect(url_for("main.admin_master_publisher"))
    row = MstPublisher(
        publisher_name=name,
        input_date=datetime.utcnow().date(),
        last_update=datetime.utcnow().date(),
    )
    db.session.add(row)
    db.session.commit()
    return redirect(url_for("main.admin_master_publisher"))


@bp.post("/admin/masterfile/penerbit/<int:row_id>/update")
@login_required
def admin_master_publisher_update(row_id: int):
    row = MstPublisher.query.get_or_404(row_id)
    data = request.get_json(silent=True) or {}
    name = (data.get("publisher_name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "Nama penerbit wajib diisi."}), 400
    row.publisher_name = name
    row.last_update = datetime.utcnow().date()
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/masterfile/penerbit/<int:row_id>/delete")
@login_required
def admin_master_publisher_delete(row_id: int):
    row = MstPublisher.query.get_or_404(row_id)
    db.session.delete(row)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/admin/masterfile/bahasa")
@login_required
def admin_master_language():
    rows = MstLanguage.query.order_by(MstLanguage.language_name.asc()).all()
    return render_template(
        "admin/master_language.html",
        title="Master Bahasa",
        crumbs="Masterfile / Bahasa Dokumen",
        active="master_language",
        rows=rows,
    )


@bp.post("/admin/masterfile/bahasa/create")
@login_required
def admin_master_language_create():
    language_id = (request.form.get("language_id") or "").strip()
    name = (request.form.get("language_name") or "").strip()
    if not language_id or not name:
        return redirect(url_for("main.admin_master_language"))
    row = MstLanguage(
        language_id=language_id,
        language_name=name,
        input_date=datetime.utcnow().date(),
        last_update=datetime.utcnow().date(),
    )
    db.session.add(row)
    db.session.commit()
    return redirect(url_for("main.admin_master_language"))


@bp.post("/admin/masterfile/bahasa/<language_id>/update")
@login_required
def admin_master_language_update(language_id: str):
    row = MstLanguage.query.get_or_404(language_id)
    data = request.get_json(silent=True) or {}
    lang_id = (data.get("language_id") or "").strip()
    name = (data.get("language_name") or "").strip()
    if not lang_id or not name:
        return jsonify({"ok": False, "error": "Kode dan nama bahasa wajib diisi."}), 400
    if lang_id != row.language_id:
        exists = MstLanguage.query.filter_by(language_id=lang_id).first()
        if exists:
            return jsonify({"ok": False, "error": "Kode bahasa sudah digunakan."}), 400
        row.language_id = lang_id
    row.language_name = name
    row.last_update = datetime.utcnow().date()
    db.session.commit()
    return jsonify({"ok": True, "language_id": row.language_id})


@bp.post("/admin/masterfile/bahasa/<language_id>/delete")
@login_required
def admin_master_language_delete(language_id: str):
    row = MstLanguage.query.get_or_404(language_id)
    db.session.delete(row)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/admin/pelaporan/statistik-koleksi")
@login_required
def admin_report_collection():
    total_titles = db.session.query(func.count(Biblio.biblio_id)).scalar() or 0
    total_items = db.session.query(func.count(Item.item_id)).scalar() or 0
    titles_with_items = (
        db.session.query(func.count(func.distinct(Item.biblio_id))).scalar() or 0
    )
    items_on_loan = (
        db.session.query(func.count(Loan.loan_id))
        .filter(Loan.is_return == 0)
        .scalar()
        or 0
    )
    items_in_collection = total_items
    by_gmd = (
        db.session.query(MstGmd.gmd_name, func.count(Biblio.biblio_id))
        .outerjoin(Biblio, Biblio.gmd_id == MstGmd.gmd_id)
        .group_by(MstGmd.gmd_name)
        .order_by(func.count(Biblio.biblio_id).desc())
        .all()
    )
    by_coll_type = (
        db.session.query(MstCollType.coll_type_name, func.count(Item.item_id))
        .outerjoin(Item, Item.coll_type_id == MstCollType.coll_type_id)
        .group_by(MstCollType.coll_type_name)
        .order_by(func.count(Item.item_id).desc())
        .all()
    )
    popular_titles = (
        db.session.query(Biblio.title, func.count(Loan.loan_id).label("cnt"))
        .outerjoin(Item, Item.biblio_id == Biblio.biblio_id)
        .outerjoin(Loan, Loan.item_code == Item.item_code)
        .group_by(Biblio.title)
        .order_by(func.count(Loan.loan_id).desc())
        .limit(10)
        .all()
    )
    return render_template(
        "admin/report_collection.html",
        title="Statistik Koleksi",
        crumbs="Pelaporan / Statistik Koleksi",
        active="report_collection",
        total_titles=total_titles,
        titles_with_items=titles_with_items,
        total_items=total_items,
        items_on_loan=items_on_loan,
        items_in_collection=items_in_collection,
        by_gmd=[(name, int(count)) for name, count in by_gmd],
        by_coll_type=[(name, int(count)) for name, count in by_coll_type],
        popular_titles=popular_titles,
    )


@bp.get("/admin/pelaporan/laporan-peminjaman")
@login_required
def admin_report_loans():
    total_loans = db.session.query(func.count(Loan.loan_id)).scalar() or 0
    by_gmd = (
        db.session.query(MstGmd.gmd_name, func.count(Loan.loan_id))
        .outerjoin(Biblio, Biblio.gmd_id == MstGmd.gmd_id)
        .outerjoin(Item, Item.biblio_id == Biblio.biblio_id)
        .outerjoin(Loan, Loan.item_code == Item.item_code)
        .group_by(MstGmd.gmd_name)
        .order_by(func.count(Loan.loan_id).desc())
        .all()
    )
    by_coll_type = (
        db.session.query(MstCollType.coll_type_name, func.count(Loan.loan_id))
        .outerjoin(Item, Item.coll_type_id == MstCollType.coll_type_id)
        .outerjoin(Loan, Loan.item_code == Item.item_code)
        .group_by(MstCollType.coll_type_name)
        .order_by(func.count(Loan.loan_id).desc())
        .all()
    )

    total_transactions = (
        db.session.query(func.count(func.distinct(Loan.loan_date))).scalar() or 0
    )
    avg_per_day = int(total_loans / total_transactions) if total_transactions else 0
    daily_max = (
        db.session.query(func.count(Loan.loan_id).label("cnt"))
        .group_by(Loan.loan_date)
        .order_by(func.count(Loan.loan_id).desc())
        .limit(1)
        .scalar()
        or 0
    )
    members_borrowing = (
        db.session.query(func.count(func.distinct(Loan.member_id))).scalar() or 0
    )
    total_members = db.session.query(func.count(Member.member_id)).scalar() or 0
    members_never = max(total_members - members_borrowing, 0)
    overdue = (
        db.session.query(func.count(Loan.loan_id))
        .filter(Loan.is_return == 0, Loan.due_date < datetime.utcnow().date())
        .scalar()
        or 0
    )

    return render_template(
        "admin/report_loans.html",
        title="Laporan Peminjaman",
        crumbs="Pelaporan / Laporan Peminjaman",
        active="report_loans",
        total_loans=total_loans,
        by_gmd=[(name, int(count)) for name, count in by_gmd],
        by_coll_type=[(name, int(count)) for name, count in by_coll_type],
        total_transactions=total_transactions,
        avg_per_day=avg_per_day,
        daily_max=daily_max,
        members_borrowing=members_borrowing,
        members_never=members_never,
        overdue=overdue,
    )


@bp.get("/admin/pelaporan/laporan-anggota")
@login_required
def admin_report_members():
    by_type = (
        db.session.query(MstMemberType.member_type_name, func.count(Member.member_id))
        .outerjoin(Member, Member.member_type_id == MstMemberType.member_type_id)
        .group_by(MstMemberType.member_type_name)
        .order_by(func.count(Member.member_id).desc())
        .all()
    )
    total_members = db.session.query(func.count(Member.member_id)).scalar() or 0
    return render_template(
        "admin/report_members.html",
        title="Laporan Anggota",
        crumbs="Pelaporan / Laporan Anggota",
        active="report_members",
        by_type=by_type,
        total_members=total_members,
    )


@bp.get("/admin/pelaporan/statistik-penggunaan")
@login_required
def admin_report_usage():
    popular = (
        db.session.query(Biblio.title, func.count(Loan.loan_id))
        .outerjoin(Item, Item.biblio_id == Biblio.biblio_id)
        .outerjoin(Loan, Loan.item_code == Item.item_code)
        .group_by(Biblio.title)
        .order_by(func.count(Loan.loan_id).desc())
        .limit(15)
        .all()
    )
    return render_template(
        "admin/report_usage.html",
        title="Statistik Penggunaan Koleksi",
        crumbs="Pelaporan / Statistik Penggunaan Koleksi",
        active="report_usage",
        popular=popular,
    )


@bp.get("/admin/pelaporan/peminjaman-klasifikasi")
@login_required
def admin_report_classification():
    rows = (
        db.session.query(Biblio.classification, func.count(Loan.loan_id))
        .outerjoin(Item, Item.biblio_id == Biblio.biblio_id)
        .outerjoin(Loan, Loan.item_code == Item.item_code)
        .group_by(Biblio.classification)
        .order_by(func.count(Loan.loan_id).desc())
        .limit(20)
        .all()
    )
    return render_template(
        "admin/report_classification.html",
        title="Peminjaman Berdasarkan Klasifikasi",
        crumbs="Pelaporan / Peminjaman Berdasarkan Klasifikasi",
        active="report_classification",
        rows=rows,
    )


@bp.get("/admin/sistem/hari-libur")
@login_required
def admin_system_holidays():
    return render_template(
        "admin/system_holidays.html",
        title="Setelan Hari Libur",
        crumbs="Sistem / Setelan Hari Libur",
        active="system_holidays",
    )


@bp.get("/admin/sistem/kelompok-pengguna")
@login_required
def admin_system_groups():
    groups = UserGroup.query.order_by(UserGroup.group_name.asc()).all()
    return render_template(
        "admin/system_groups.html",
        title="Kelompok Pengguna",
        crumbs="Sistem / Kelompok Pengguna",
        active="system_groups",
        rows=groups,
    )


@bp.get("/admin/sistem/pengguna")
@login_required
def admin_system_users():
    users = User.query.order_by(User.username.asc()).all()
    return render_template(
        "admin/system_users.html",
        title="Pustakawan & Pengguna Sistem",
        crumbs="Sistem / Pustakawan & Pengguna Sistem",
        active="system_users",
        rows=users,
    )


@bp.post("/admin/anggota/create")
@login_required
def admin_member_create():
    data = request.get_json(silent=True) or {}
    member_id = (data.get("member_id") or "").strip()
    member_name = (data.get("member_name") or "").strip()
    expire_date_raw = (data.get("expire_date") or "").strip()
    if not member_id or not member_name or not expire_date_raw:
        return jsonify({"ok": False, "error": "ID, Nama, dan Berlaku Hingga wajib diisi."}), 400

    exists = Member.query.filter_by(member_id=member_id).first()
    if exists:
        return jsonify({"ok": False, "error": "ID anggota sudah digunakan."}), 400

    member = Member(
        member_id=member_id,
        member_name=member_name,
        member_type_id=data.get("member_type_id") or None,
        expire_date=expire_date_raw,
        inst_name=data.get("inst_name"),
        input_date=datetime.utcnow().date(),
        last_update=datetime.utcnow().date(),
        gender=0,
        is_pending=1 if data.get("status") == "inactive" else 0,
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/anggota/<member_id>/update")
@login_required
def admin_member_update(member_id: str):
    member = Member.query.get_or_404(member_id)
    data = request.get_json(silent=True) or {}
    name = (data.get("member_name") or "").strip()
    expire_date_raw = (data.get("expire_date") or "").strip()
    if not name or not expire_date_raw:
        return jsonify({"ok": False, "error": "Nama dan Berlaku Hingga wajib diisi."}), 400

    member.member_name = name
    member.member_type_id = data.get("member_type_id") or None
    member.expire_date = expire_date_raw
    member.inst_name = data.get("inst_name")
    member.is_pending = 1 if data.get("status") == "inactive" else 0
    member.last_update = datetime.utcnow().date()
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/anggota/delete")
@login_required
def admin_member_delete():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []
    if not isinstance(ids, list) or not ids:
        return jsonify({"ok": False, "error": "ID tidak valid."}), 400

    (
        db.session.query(Member)
        .filter(Member.member_id.in_(ids))
        .delete(synchronize_session=False)
    )
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/admin/transaksi")
@login_required
def admin_transaksi():
    return render_template(
        "admin/transaction.html",
        title="Mulai Transaksi",
        crumbs="Mulai Transaksi",
        active="transaction",
    )


def _build_member_payload(member: Member):
    member_type = None
    if member.member_type_id:
        member_type = MstMemberType.query.get(member.member_type_id)
    return {
        "member_id": member.member_id,
        "member_name": member.member_name,
        "member_email": member.member_email or "",
        "member_type_name": member_type.member_type_name if member_type else "-",
        "register_date": member.register_date.strftime("%d %b %Y")
        if member.register_date
        else "-",
        "expire_date": member.expire_date.strftime("%d %b %Y")
        if member.expire_date
        else "-",
        "fine_each_day": member_type.fine_each_day if member_type else 0,
    }


def _get_loan_data(member_id: str):
    current = []
    history = []
    fines_items = []
    fines_total = 0

    loans = (
        db.session.query(Loan, Item, Biblio)
        .outerjoin(Item, Item.item_code == Loan.item_code)
        .outerjoin(Biblio, Biblio.biblio_id == Item.biblio_id)
        .filter(Loan.member_id == member_id)
        .order_by(Loan.loan_date.desc())
        .all()
    )
    member = Member.query.get(member_id)
    fine_each_day = 0
    if member and member.member_type_id:
        mt = MstMemberType.query.get(member.member_type_id)
        fine_each_day = mt.fine_each_day if mt else 0

    today = datetime.utcnow().date()

    for loan, item, biblio in loans:
        title = biblio.title if biblio else "-"
        item_code = loan.item_code
        loan_date = loan.loan_date.strftime("%d %b %Y") if loan.loan_date else "-"
        due_date = loan.due_date.strftime("%d %b %Y") if loan.due_date else "-"
        return_date = loan.return_date.strftime("%d %b %Y") if loan.return_date else "-"

        entry = {
            "loan_id": loan.loan_id,
            "title": title,
            "item_code": item_code,
            "loan_date": loan_date,
            "due_date": due_date,
            "return_date": return_date if loan.is_return else None,
            "status": "returned" if loan.is_return else "active",
            "status_label": "Selesai" if loan.is_return else "Aktif",
            "fine_amount": 0,
        }

        if loan.is_return:
            history.append(entry)
        else:
            current.append(entry)
            if loan.due_date and loan.due_date < today and fine_each_day:
                days_late = (today - loan.due_date).days
                amount = days_late * fine_each_day
                fines_total += amount
                entry["fine_amount"] = amount
                fines_items.append(
                    {
                        "title": title,
                        "item_code": item_code,
                        "days_late": days_late,
                        "amount": amount,
                        "source": "overdue",
                    }
                )

    # Include fines recorded in fines table
    fines_rows = (
        db.session.query(Fines)
        .filter(Fines.member_id == member_id)
        .order_by(Fines.fines_date.desc(), Fines.fines_id.desc())
        .all()
    )
    for fine in fines_rows:
        debet = int(fine.debet or 0)
        credit = int(fine.credit or 0)
        amount = debet - credit
        if amount <= 0:
            continue
        fines_total += amount
        fines_items.append(
            {
                "title": fine.description or "Denda",
                "item_code": "-",
                "days_late": None,
                "amount": amount,
                "source": "table",
            }
        )

    return current, history, {"total": fines_total, "items": fines_items}


@bp.post("/admin/transaksi/member")
@login_required
def admin_transaksi_member():
    data = request.get_json(silent=True) or {}
    member_id = (data.get("member_id") or "").strip()
    if not member_id:
        return jsonify({"ok": False, "error": "ID anggota wajib diisi."}), 400

    member = Member.query.get(member_id)
    if not member:
        return jsonify({"ok": False, "error": "Anggota tidak ditemukan."}), 404

    current, history, fines = _get_loan_data(member_id)
    return jsonify(
        {
            "ok": True,
            "member": _build_member_payload(member),
            "current": current,
            "history": history,
            "fines": fines,
        }
    )


@bp.post("/admin/transaksi/loan")
@login_required
def admin_transaksi_loan():
    data = request.get_json(silent=True) or {}
    member_id = (data.get("member_id") or "").strip()
    item_code = (data.get("item_code") or "").strip()
    if not member_id or not item_code:
        return jsonify({"ok": False, "error": "ID anggota dan kode eksemplar wajib diisi."}), 400

    member = Member.query.get(member_id)
    if not member:
        return jsonify({"ok": False, "error": "Anggota tidak ditemukan."}), 404

    item = Item.query.filter(
        or_(Item.item_code == item_code, Item.inventory_code == item_code)
    ).first()
    if not item:
        return jsonify({"ok": False, "error": "Eksemplar tidak ditemukan."}), 404

    active_loan = Loan.query.filter_by(item_code=item.item_code, is_return=0).first()
    if active_loan:
        return jsonify({"ok": False, "error": "Eksemplar sedang dipinjam."}), 400

    loan_days = 14
    if member.member_type_id:
        mt = MstMemberType.query.get(member.member_type_id)
        if mt and mt.loan_periode:
            loan_days = mt.loan_periode

    today = datetime.utcnow().date()
    due_date = today + timedelta(days=loan_days)

    loan = Loan(
        item_code=item.item_code,
        member_id=member_id,
        loan_date=today,
        due_date=due_date,
        renewed=0,
        loan_rules_id=0,
        actual=None,
        is_lent=1,
        is_return=0,
        return_date=None,
        input_date=datetime.utcnow(),
        last_update=datetime.utcnow(),
        uid=0,
    )
    db.session.add(loan)
    db.session.commit()

    current, history, fines = _get_loan_data(member_id)
    return jsonify({"ok": True, "current": current, "history": history, "fines": fines})


@bp.post("/admin/transaksi/return")
@login_required
def admin_transaksi_return():
    data = request.get_json(silent=True) or {}
    loan_id = data.get("loan_id")
    if not loan_id:
        return jsonify({"ok": False, "error": "Loan ID tidak valid."}), 400

    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({"ok": False, "error": "Data pinjaman tidak ditemukan."}), 404

    today = datetime.utcnow().date()
    loan.is_return = 1
    loan.is_lent = 0
    loan.return_date = today
    loan.actual = today
    loan.last_update = datetime.utcnow()
    db.session.commit()

    current, history, fines = _get_loan_data(loan.member_id)
    return jsonify({"ok": True, "current": current, "history": history, "fines": fines})


@bp.get("/admin/aturan-peminjaman")
@login_required
def admin_loan_rules():
    rules = MstLoanRules.query.order_by(MstLoanRules.loan_rules_id.desc()).all()
    member_types = MstMemberType.query.order_by(MstMemberType.member_type_name.asc()).all()
    gmds = MstGmd.query.order_by(MstGmd.gmd_name.asc()).all()

    member_type_map = {m.member_type_id: m.member_type_name for m in member_types}
    gmd_map = {g.gmd_id: g.gmd_name for g in gmds}

    rows = []
    for rule in rules:
        rows.append(
            {
                "loan_rules_id": rule.loan_rules_id,
                "member_type_id": rule.member_type_id,
                "member_type_name": member_type_map.get(rule.member_type_id, "-"),
                "gmd_id": rule.gmd_id,
                "gmd_name": gmd_map.get(rule.gmd_id, "Semua GMD") if rule.gmd_id else "Semua GMD",
                "loan_limit": rule.loan_limit,
                "loan_periode": rule.loan_periode,
                "fine_each_day": 500,
                "extend": rule.loan_periode,
            }
        )

    return render_template(
        "admin/loan_rules.html",
        title="Aturan Peminjaman",
        crumbs="Aturan Peminjaman",
        active="loan_rules",
        rows=rows,
        member_types=member_types,
        gmds=gmds,
    )


@bp.post("/admin/aturan-peminjaman/create")
@login_required
def admin_loan_rules_create():
    data = request.get_json(silent=True) or {}
    member_type_id = int(data.get("member_type_id") or 0)
    gmd_id = int(data.get("gmd_id") or 0)
    if not member_type_id:
        return jsonify({"ok": False, "error": "Tipe anggota wajib diisi."}), 400

    rule = MstLoanRules(
        member_type_id=member_type_id,
        gmd_id=gmd_id,
        loan_limit=int(data.get("loan_limit") or 0),
        loan_periode=int(data.get("loan_periode") or 0),
        coll_type_id=0,
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/aturan-peminjaman/<int:loan_rules_id>/update")
@login_required
def admin_loan_rules_update(loan_rules_id: int):
    data = request.get_json(silent=True) or {}
    rule = MstLoanRules.query.get_or_404(loan_rules_id)
    rule.member_type_id = int(data.get("member_type_id") or 0)
    rule.gmd_id = int(data.get("gmd_id") or 0)
    rule.loan_limit = int(data.get("loan_limit") or 0)
    rule.loan_periode = int(data.get("loan_periode") or 0)
    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/aturan-peminjaman/<int:loan_rules_id>/delete")
@login_required
def admin_loan_rules_delete(loan_rules_id: int):
    rule = MstLoanRules.query.get_or_404(loan_rules_id)
    db.session.delete(rule)
    db.session.commit()
    return jsonify({"ok": True})


@bp.get("/admin/pengembalian-kilat")
@login_required
def admin_quick_return():
    return render_template(
        "admin/quick_return.html",
        title="Pengembalian Kilat",
        crumbs="Pengembalian Kilat",
        active="quick_return",
    )


@bp.post("/admin/pengembalian-kilat")
@login_required
def admin_quick_return_post():
    data = request.get_json(silent=True) or {}
    code = (data.get("item_code") or "").strip()
    if not code:
        return jsonify({"ok": False, "error": "Kode eksemplar wajib diisi."}), 400

    loan = Loan.query.filter(
        and_(
            Loan.item_code == code,
            Loan.is_return == 0,
        )
    ).first()
    if not loan:
        return jsonify({"ok": False, "error": "Eksemplar tidak sedang dipinjam."}), 404

    member = Member.query.get(loan.member_id)
    if not member:
        return jsonify({"ok": False, "error": "Data anggota tidak ditemukan."}), 404

    today = datetime.utcnow().date()
    loan.is_return = 1
    loan.is_lent = 0
    loan.return_date = today
    loan.actual = today
    loan.last_update = datetime.utcnow()
    db.session.commit()

    return jsonify(
        {
            "ok": True,
            "member_name": member.member_name,
            "member_id": member.member_id,
            "item_code": loan.item_code,
        }
    )


@bp.get("/opac/biblio/<int:biblio_id>")
def opac_biblio_detail(biblio_id: int):
    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS biblio_view (
                biblio_id INT PRIMARY KEY,
                views INT NOT NULL DEFAULT 0,
                last_viewed DATETIME NULL
            )
            """
        )
    )
    db.session.commit()

    biblio = Biblio.query.get_or_404(biblio_id)
    search = SearchBiblio.query.filter_by(biblio_id=biblio_id).first()

    items = Item.query.filter_by(biblio_id=biblio_id).all()
    loans = (
        Loan.query.filter(Loan.item_code.in_([i.item_code for i in items if i.item_code]))
        .filter(Loan.is_return == 0)
        .all()
    )
    loan_map = {l.item_code: l for l in loans}

    item_rows = []
    for item in items:
        loan = loan_map.get(item.item_code)
        status = "Tersedia" if not loan else "Dipinjam"
        due = loan.due_date.strftime("%d %b %Y") if loan and loan.due_date else "-"
        item_rows.append(
            {
                "item_code": item.item_code or "-",
                "call_number": item.call_number or "-",
                "location": item.location_id or "-",
                "status": status,
                "due_date": due,
            }
        )

    copies = len(items)
    view = BiblioView.query.get(biblio_id)
    if not view:
        view = BiblioView(biblio_id=biblio_id, views=1, last_viewed=datetime.utcnow())
        db.session.add(view)
    else:
        view.views += 1
        view.last_viewed = datetime.utcnow()
    db.session.commit()

    view_count = view.views

    return jsonify(
        {
            "title": biblio.title,
            "author": search.author if search and search.author else "-",
            "year": biblio.publish_year or "-",
            "isbn": biblio.isbn_issn or "-",
            "call_number": biblio.call_number or "-",
            "copies": copies,
            "views": view_count,
            "input_date": biblio.input_date.strftime("%d %b %Y")
            if biblio.input_date
            else "-",
            "items": item_rows,
        }
    )


@bp.post("/admin/label-barcode/items")
@login_required
def admin_items_label_data():
    data = request.get_json(silent=True) or {}
    ids = data.get("ids") or []
    if not isinstance(ids, list) or not ids:
        return jsonify({"items": []})

    items = (
        db.session.query(Item, Biblio)
        .outerjoin(Biblio, Biblio.biblio_id == Item.biblio_id)
        .filter(Item.item_id.in_(ids))
        .all()
    )
    payload = []
    for item, biblio in items:
        payload.append(
            {
                "id": item.item_id,
                "code": item.item_code or item.inventory_code or "",
                "title": biblio.title if biblio else "",
                "call_number": item.call_number or "",
            }
        )
    return jsonify({"items": payload})


@bp.route("/admin/bibliografi/new", methods=["GET", "POST"])
@login_required
def admin_biblio_new():
    message = None
    form = {}

    gmds = MstGmd.query.order_by(MstGmd.gmd_name.asc()).all()
    publishers = MstPublisher.query.order_by(MstPublisher.publisher_name.asc()).all()
    places = MstPlace.query.order_by(MstPlace.place_name.asc()).all()
    languages = MstLanguage.query.order_by(MstLanguage.language_name.asc()).all()
    coll_types = MstCollType.query.order_by(MstCollType.coll_type_name.asc()).all()
    item_statuses = MstItemStatus.query.order_by(MstItemStatus.item_status_name.asc()).all()
    suppliers = MstSupplier.query.order_by(MstSupplier.supplier_name.asc()).all()
    frequencies = MstFrequency.query.order_by(MstFrequency.frequency.asc()).all()

    if request.method == "POST":
        form = request.form
        title = request.form.get("title", "").strip()
        if not title:
            message = "Judul wajib diisi."
        else:
            labels = request.form.getlist("labels")
            biblio = Biblio(
                title=title,
                sor=request.form.get("sor"),
                edition=request.form.get("edition"),
                isbn_issn=request.form.get("isbn_issn"),
                publisher_id=request.form.get("publisher_id") or None,
                publish_year=request.form.get("publish_year"),
                collation=request.form.get("collation"),
                series_title=request.form.get("series_title"),
                call_number=request.form.get("call_number"),
                language_id=request.form.get("language_id") or "en",
                publish_place_id=request.form.get("publish_place_id") or None,
                classification=request.form.get("classification"),
                notes=request.form.get("notes"),
                image=request.form.get("image"),
                opac_hide=int(request.form.get("opac_hide", 0)),
                promoted=int(request.form.get("promoted", 0)),
                labels=",".join(labels) if labels else None,
                frequency_id=int(request.form.get("frequency_id") or 0),
                spec_detail_info=request.form.get("spec_detail_info"),
                gmd_id=request.form.get("gmd_id") or None,
                input_date=datetime.utcnow(),
                last_update=datetime.utcnow(),
            )

            db.session.add(biblio)
            db.session.flush()

            items = []
            for key in request.form.keys():
                if key.startswith("items-") and key.endswith("-inventory_code"):
                    index = key.split("-")[1]
                    items.append(index)

            for index in items:
                inventory_code = request.form.get(f"items-{index}-inventory_code", "").strip()
                if not inventory_code:
                    continue
                if len(inventory_code) > 20:
                    message = "Kode inventaris terlalu panjang (maks 20 karakter)."
                    break

                item = Item(
                    biblio_id=biblio.biblio_id,
                    call_number=request.form.get(f"items-{index}-call_number"),
                    coll_type_id=request.form.get(f"items-{index}-coll_type_id") or None,
                    item_code=inventory_code,
                    inventory_code=inventory_code,
                    received_date=request.form.get(f"items-{index}-received_date") or None,
                    supplier_id=request.form.get(f"items-{index}-supplier_id") or None,
                    order_no=request.form.get(f"items-{index}-order_no"),
                    location_id=request.form.get(f"items-{index}-location_id"),
                    item_status_id=request.form.get(f"items-{index}-item_status_id"),
                    site=request.form.get(f"items-{index}-site"),
                    source=int(request.form.get(f"items-{index}-source") or 0),
                    invoice=request.form.get(f"items-{index}-invoice"),
                    price=request.form.get(f"items-{index}-price") or None,
                    invoice_date=request.form.get(f"items-{index}-invoice_date") or None,
                    input_date=datetime.utcnow(),
                    last_update=datetime.utcnow(),
                )
                db.session.add(item)

            if not message:
                db.session.commit()
                return redirect(url_for("main.admin_biblio"))
            db.session.rollback()

    return render_template(
        "admin/biblio_form.html",
        title="Tambah Bibliografi",
        crumbs="Tambah Bibliografi",
        active="biblio",
        message=message,
        form=form,
        labels_set=set(),
        gmds=gmds,
        frequencies=frequencies,
        publishers=publishers,
        places=places,
        languages=languages,
        coll_types=coll_types,
        item_statuses=item_statuses,
        suppliers=suppliers,
    )


@bp.route("/admin/bibliografi/delete", methods=["POST"])
@login_required
def admin_biblio_delete():
    ids_raw = request.form.get("ids", "")
    ids = [int(x) for x in ids_raw.split(",") if x.strip().isdigit()]
    if not ids:
        return redirect(url_for("main.admin_biblio"))

    (
        db.session.query(Item)
        .filter(Item.biblio_id.in_(ids))
        .delete(synchronize_session=False)
    )
    (
        db.session.query(SearchBiblio)
        .filter(SearchBiblio.biblio_id.in_(ids))
        .delete(synchronize_session=False)
    )
    (
        db.session.query(Biblio)
        .filter(Biblio.biblio_id.in_(ids))
        .delete(synchronize_session=False)
    )
    db.session.commit()

    return redirect(url_for("main.admin_biblio"))


@bp.route("/admin/bibliografi/<int:biblio_id>/edit", methods=["GET", "POST"])
@login_required
def admin_biblio_edit(biblio_id: int):
    biblio = Biblio.query.get_or_404(biblio_id)
    search_biblio = SearchBiblio.query.filter_by(biblio_id=biblio_id).first()
    items_existing = Item.query.filter_by(biblio_id=biblio_id).all()

    form = {
        "title": biblio.title,
        "author": search_biblio.author if search_biblio else "",
        "topic": search_biblio.topic if search_biblio else "",
        "sor": biblio.sor or "",
        "edition": biblio.edition or "",
        "spec_detail_info": biblio.spec_detail_info or "",
        "gmd_id": str(biblio.gmd_id) if biblio.gmd_id else "",
        "frequency_id": str(biblio.frequency_id) if biblio.frequency_id else "",
        "isbn_issn": biblio.isbn_issn or "",
        "publisher_id": str(biblio.publisher_id) if biblio.publisher_id else "",
        "publish_year": biblio.publish_year or "",
        "publish_place_id": str(biblio.publish_place_id) if biblio.publish_place_id else "",
        "collation": biblio.collation or "",
        "series_title": biblio.series_title or "",
        "classification": biblio.classification or "",
        "call_number": biblio.call_number or "",
        "language_id": biblio.language_id or "en",
        "notes": biblio.notes or "",
        "image": biblio.image or "",
        "opac_hide": str(biblio.opac_hide or 0),
        "promoted": str(biblio.promoted or 0),
        "labels": biblio.labels or "",
    }

    message = None

    gmds = MstGmd.query.order_by(MstGmd.gmd_name.asc()).all()
    publishers = MstPublisher.query.order_by(MstPublisher.publisher_name.asc()).all()
    places = MstPlace.query.order_by(MstPlace.place_name.asc()).all()
    languages = MstLanguage.query.order_by(MstLanguage.language_name.asc()).all()
    coll_types = MstCollType.query.order_by(MstCollType.coll_type_name.asc()).all()
    item_statuses = MstItemStatus.query.order_by(MstItemStatus.item_status_name.asc()).all()
    suppliers = MstSupplier.query.order_by(MstSupplier.supplier_name.asc()).all()
    frequencies = MstFrequency.query.order_by(MstFrequency.frequency.asc()).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            message = "Judul wajib diisi."
        else:
            labels = request.form.getlist("labels")
            biblio.title = title
            biblio.sor = request.form.get("sor")
            biblio.edition = request.form.get("edition")
            biblio.isbn_issn = request.form.get("isbn_issn")
            biblio.publisher_id = request.form.get("publisher_id") or None
            biblio.publish_year = request.form.get("publish_year")
            biblio.collation = request.form.get("collation")
            biblio.series_title = request.form.get("series_title")
            biblio.call_number = request.form.get("call_number")
            biblio.language_id = request.form.get("language_id") or "en"
            biblio.publish_place_id = request.form.get("publish_place_id") or None
            biblio.classification = request.form.get("classification")
            biblio.notes = request.form.get("notes")
            biblio.image = request.form.get("image")
            biblio.opac_hide = int(request.form.get("opac_hide", 0))
            biblio.promoted = int(request.form.get("promoted", 0))
            biblio.labels = ",".join(labels) if labels else None
            biblio.frequency_id = int(request.form.get("frequency_id") or 0)
            biblio.spec_detail_info = request.form.get("spec_detail_info")
            biblio.gmd_id = request.form.get("gmd_id") or None
            biblio.last_update = datetime.utcnow()

            items = []
            for key in request.form.keys():
                if key.startswith("items-") and key.endswith("-inventory_code"):
                    index = key.split("-")[1]
                    items.append(index)

            for index in items:
                inventory_code = request.form.get(f"items-{index}-inventory_code", "").strip()
                if not inventory_code:
                    continue
                if len(inventory_code) > 20:
                    message = "Kode inventaris terlalu panjang (maks 20 karakter)."
                    break

                item = Item(
                    biblio_id=biblio.biblio_id,
                    call_number=request.form.get(f"items-{index}-call_number"),
                    coll_type_id=request.form.get(f"items-{index}-coll_type_id") or None,
                    item_code=inventory_code,
                    inventory_code=inventory_code,
                    received_date=request.form.get(f"items-{index}-received_date") or None,
                    supplier_id=request.form.get(f"items-{index}-supplier_id") or None,
                    order_no=request.form.get(f"items-{index}-order_no"),
                    location_id=request.form.get(f"items-{index}-location_id"),
                    item_status_id=request.form.get(f"items-{index}-item_status_id"),
                    site=request.form.get(f"items-{index}-site"),
                    source=int(request.form.get(f"items-{index}-source") or 0),
                    invoice=request.form.get(f"items-{index}-invoice"),
                    price=request.form.get(f"items-{index}-price") or None,
                    invoice_date=request.form.get(f"items-{index}-invoice_date") or None,
                    input_date=datetime.utcnow(),
                    last_update=datetime.utcnow(),
                )
                db.session.add(item)

            if not message:
                db.session.commit()
                return redirect(url_for("main.admin_biblio"))
            db.session.rollback()

    labels_set = set(filter(None, form["labels"].split(",")))

    return render_template(
        "admin/biblio_form.html",
        title="Edit Bibliografi",
        crumbs="Edit Bibliografi",
        active="biblio",
        message=message,
        form=form,
        labels_set=labels_set,
        gmds=gmds,
        frequencies=frequencies,
        publishers=publishers,
        places=places,
        languages=languages,
        coll_types=coll_types,
        item_statuses=item_statuses,
        suppliers=suppliers,
        items_existing=items_existing,
        edit_mode=True,
    )


@bp.post("/admin/items/<int:item_id>/update")
@login_required
def admin_item_update(item_id: int):
    item = Item.query.get_or_404(item_id)
    data = request.get_json(silent=True) or {}

    inventory_code = (data.get("inventory_code") or "").strip()
    if not inventory_code:
        return jsonify({"error": "Kode inventaris wajib diisi."}), 400
    if len(inventory_code) > 20:
        return jsonify({"error": "Kode inventaris terlalu panjang (maks 20 karakter)."}), 400

    item.call_number = data.get("call_number")
    item.inventory_code = inventory_code
    item.item_code = inventory_code
    item.location_id = data.get("location_id")
    item.site = data.get("site")
    item.coll_type_id = data.get("coll_type_id") or None
    item.item_status_id = data.get("item_status_id") or None
    item.order_no = data.get("order_no")
    item.received_date = data.get("received_date") or None
    item.supplier_id = data.get("supplier_id") or None
    item.source = int(data.get("source") or 0)
    item.invoice = data.get("invoice")
    item.invoice_date = data.get("invoice_date") or None
    item.price = data.get("price") or None
    item.last_update = datetime.utcnow()

    db.session.commit()
    return jsonify({"ok": True})


@bp.post("/admin/items/<int:item_id>/delete")
@login_required
def admin_item_delete(item_id: int):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"ok": True})
