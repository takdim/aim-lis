from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class Biblio(db.Model):
    __tablename__ = "biblio"
    biblio_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gmd_id = db.Column(db.Integer, index=True)
    title = db.Column(db.Text, nullable=False)
    sor = db.Column(db.String(200))
    edition = db.Column(db.String(50))
    isbn_issn = db.Column(db.String(32))
    publisher_id = db.Column(db.Integer)
    publish_year = db.Column(db.String(20))
    collation = db.Column(db.String(100))
    series_title = db.Column(db.String(200))
    call_number = db.Column(db.String(50))
    language_id = db.Column(db.String(5), default="en")
    source = db.Column(db.String(3))
    publish_place_id = db.Column(db.Integer)
    classification = db.Column(db.String(40), index=True)
    notes = db.Column(db.Text)
    image = db.Column(db.String(100))
    file_att = db.Column(db.String(255))
    opac_hide = db.Column(db.SmallInteger, default=0)
    promoted = db.Column(db.SmallInteger, default=0)
    labels = db.Column(db.Text)
    frequency_id = db.Column(db.Integer, nullable=False, default=0)
    spec_detail_info = db.Column(db.Text)
    content_type_id = db.Column(db.Integer)
    media_type_id = db.Column(db.Integer)
    carrier_type_id = db.Column(db.Integer)
    input_date = db.Column(db.DateTime)
    last_update = db.Column(db.DateTime)
    uid = db.Column(db.Integer, index=True)


class Item(db.Model):
    __tablename__ = "item"
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    biblio_id = db.Column(db.Integer, index=True)
    call_number = db.Column(db.String(50))
    coll_type_id = db.Column(db.Integer)
    item_code = db.Column(db.String(20), unique=True)
    inventory_code = db.Column(db.String(200))
    received_date = db.Column(db.Date)
    supplier_id = db.Column(db.String(6))
    order_no = db.Column(db.String(20))
    location_id = db.Column(db.String(3))
    order_date = db.Column(db.Date)
    item_status_id = db.Column(db.String(3))
    site = db.Column(db.String(50))
    source = db.Column(db.Integer, nullable=False, default=0)
    invoice = db.Column(db.String(20))
    price = db.Column(db.Integer)
    price_currency = db.Column(db.String(10))
    invoice_date = db.Column(db.Date)
    input_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime)
    uid = db.Column(db.Integer)


class BiblioAttachment(db.Model):
    __tablename__ = "biblio_attachment"
    biblio_id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, primary_key=True)
    placement = db.Column(db.Enum("link", "popup", "embed"))
    access_type = db.Column(db.Enum("public", "private"), nullable=False)
    access_limit = db.Column(db.Text)


class BiblioAuthor(db.Model):
    __tablename__ = "biblio_author"
    biblio_id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False, default=1)


class BiblioTopic(db.Model):
    __tablename__ = "biblio_topic"
    biblio_id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False, default=1)


class BiblioRelation(db.Model):
    __tablename__ = "biblio_relation"
    biblio_id = db.Column(db.Integer, primary_key=True)
    rel_biblio_id = db.Column(db.Integer, primary_key=True)
    rel_type = db.Column(db.Integer, default=1)


class BiblioCustom(db.Model):
    __tablename__ = "biblio_custom"
    biblio_id = db.Column(db.Integer, primary_key=True)


class Member(db.Model):
    __tablename__ = "member"
    member_id = db.Column(db.String(20), primary_key=True)
    member_name = db.Column(db.String(100), nullable=False, index=True)
    gender = db.Column(db.Integer, nullable=False)
    birth_date = db.Column(db.Date)
    member_type_id = db.Column(db.Integer, index=True)
    member_address = db.Column(db.String(255))
    member_mail_address = db.Column(db.String(255))
    member_email = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    inst_name = db.Column(db.String(100))
    is_new = db.Column(db.Integer)
    member_image = db.Column(db.String(200))
    pin = db.Column(db.String(50))
    member_phone = db.Column(db.String(50))
    member_fax = db.Column(db.String(50))
    member_since_date = db.Column(db.Date)
    register_date = db.Column(db.Date)
    expire_date = db.Column(db.Date, nullable=False)
    member_notes = db.Column(db.Text)
    is_pending = db.Column(db.SmallInteger, nullable=False, default=0)
    mpasswd = db.Column(db.String(64))
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(20))
    input_date = db.Column(db.Date)
    last_update = db.Column(db.Date)


class Loan(db.Model):
    __tablename__ = "loan"
    loan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    item_code = db.Column(db.String(20), index=True)
    member_id = db.Column(db.String(20), index=True)
    loan_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    renewed = db.Column(db.Integer, nullable=False, default=0)
    loan_rules_id = db.Column(db.Integer, nullable=False, default=0)
    actual = db.Column(db.Date)
    is_lent = db.Column(db.Integer, nullable=False, default=0)
    is_return = db.Column(db.Integer, nullable=False, default=0)
    return_date = db.Column(db.Date)
    input_date = db.Column(db.DateTime)
    last_update = db.Column(db.DateTime)
    uid = db.Column(db.Integer)


class Fines(db.Model):
    __tablename__ = "fines"
    fines_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fines_date = db.Column(db.Date, nullable=False)
    member_id = db.Column(db.String(20), nullable=False, index=True)
    debet = db.Column(db.Integer, default=0)
    credit = db.Column(db.Integer, default=0)
    description = db.Column(db.String(255))


class Reserve(db.Model):
    __tablename__ = "reserve"
    reserve_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.String(20), nullable=False, index=True)
    biblio_id = db.Column(db.Integer, nullable=False)
    item_code = db.Column(db.String(20), nullable=False, index=True)
    reserve_date = db.Column(db.DateTime, nullable=False)


class MemberCustom(db.Model):
    __tablename__ = "member_custom"
    member_id = db.Column(db.String(20), primary_key=True)


class MstAuthor(db.Model):
    __tablename__ = "mst_author"
    author_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_name = db.Column(db.String(100), nullable=False)
    author_year = db.Column(db.String(20))
    authority_type = db.Column(db.Enum("p", "o", "c"), default="p")
    auth_list = db.Column(db.String(20))
    input_date = db.Column(db.Date, nullable=False)
    last_update = db.Column(db.Date)


class MstPublisher(db.Model):
    __tablename__ = "mst_publisher"
    publisher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    publisher_name = db.Column(db.String(100), nullable=False, unique=True)
    input_date = db.Column(db.Date)
    last_update = db.Column(db.Date)


class MstTopic(db.Model):
    __tablename__ = "mst_topic"
    topic_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(50), nullable=False)
    topic_type = db.Column(db.Enum("t", "g", "n", "tm", "gr", "oc"), nullable=False)
    auth_list = db.Column(db.String(20))
    classification = db.Column(db.String(50), nullable=False)
    input_date = db.Column(db.Date)
    last_update = db.Column(db.Date)


class MstPlace(db.Model):
    __tablename__ = "mst_place"
    place_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    place_name = db.Column(db.String(30), nullable=False, unique=True)
    input_date = db.Column(db.Date)
    last_update = db.Column(db.Date)


class MstLanguage(db.Model):
    __tablename__ = "mst_language"
    language_id = db.Column(db.String(5), primary_key=True)
    language_name = db.Column(db.String(20), nullable=False, unique=True)
    input_date = db.Column(db.Date)
    last_update = db.Column(db.Date)


class MstGmd(db.Model):
    __tablename__ = "mst_gmd"
    gmd_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gmd_code = db.Column(db.String(3), unique=True)
    gmd_name = db.Column(db.String(30), nullable=False, unique=True)
    icon_image = db.Column(db.String(100))
    input_date = db.Column(db.Date, nullable=False)
    last_update = db.Column(db.Date)


class MstItemStatus(db.Model):
    __tablename__ = "mst_item_status"
    item_status_id = db.Column(db.String(3), primary_key=True)
    item_status_name = db.Column(db.String(30), nullable=False, unique=True)
    rules = db.Column(db.String(255))
    no_loan = db.Column(db.SmallInteger, nullable=False, default=0)
    skip_stock_take = db.Column(db.SmallInteger, nullable=False, default=0)
    input_date = db.Column(db.Date)
    last_update = db.Column(db.Date)


class MstCollType(db.Model):
    __tablename__ = "mst_coll_type"
    coll_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    coll_type_name = db.Column(db.String(30), nullable=False, unique=True)
    input_date = db.Column(db.Date)
    last_update = db.Column(db.Date)


class MstCarrierType(db.Model):
    __tablename__ = "mst_carrier_type"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    carrier_type = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(5), nullable=False, index=True)
    code2 = db.Column(db.String(1), nullable=False)
    input_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)


class MstContentType(db.Model):
    __tablename__ = "mst_content_type"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_type = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(5), nullable=False, index=True)
    code2 = db.Column(db.String(1), nullable=False)
    input_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)


class MstMediaType(db.Model):
    __tablename__ = "mst_media_type"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    media_type = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(5), nullable=False, index=True)
    code2 = db.Column(db.String(1), nullable=False)
    input_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)


class MstFrequency(db.Model):
    __tablename__ = "mst_frequency"
    frequency_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    frequency = db.Column(db.String(25), nullable=False)
    language_prefix = db.Column(db.String(5))
    time_increment = db.Column(db.SmallInteger)
    time_unit = db.Column(db.Enum("day", "week", "month", "year"), default="day")
    input_date = db.Column(db.Date, nullable=False)
    last_update = db.Column(db.Date, nullable=False)


class MstLabel(db.Model):
    __tablename__ = "mst_label"
    label_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label_name = db.Column(db.String(20), nullable=False, unique=True)
    label_desc = db.Column(db.String(50))
    label_image = db.Column(db.String(200), nullable=False)
    input_date = db.Column(db.Date, nullable=False)
    last_update = db.Column(db.Date, nullable=False)


class MstSupplier(db.Model):
    __tablename__ = "mst_supplier"
    supplier_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    supplier_name = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(100))
    phone = db.Column(db.String(14))
    contact = db.Column(db.String(30))
    input_date = db.Column(db.Date)
    last_update = db.Column(db.Date)


class MstMemberType(db.Model):
    __tablename__ = "mst_member_type"
    member_type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_type_name = db.Column(db.String(50), nullable=False, unique=True)
    loan_limit = db.Column(db.Integer, nullable=False)
    loan_periode = db.Column(db.Integer, nullable=False)
    reborrow_limit = db.Column(db.Integer)
    reserve_limit = db.Column(db.Integer)
    member_periode = db.Column(db.Integer, nullable=False)
    fine_each_day = db.Column(db.Integer, nullable=False)
    input_date = db.Column(db.Date, nullable=False)
    last_update = db.Column(db.Date)


class MstLoanRules(db.Model):
    __tablename__ = "mst_loan_rules"
    loan_rules_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_type_id = db.Column(db.Integer, nullable=False, default=0)
    coll_type_id = db.Column(db.Integer, default=0)
    gmd_id = db.Column(db.Integer, default=0)
    loan_limit = db.Column(db.Integer, default=0)
    loan_periode = db.Column(db.Integer, default=0)


class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    realname = db.Column(db.String(100), nullable=False)
    passwd = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(200))
    groups = db.Column(db.String(200))
    last_login = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(15))


class UserGroup(db.Model):
    __tablename__ = "user_group"
    group_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_name = db.Column(db.String(30), nullable=False, unique=True)
    input_date = db.Column(db.Date)
    last_update = db.Column(db.Date)


class VisitorCount(db.Model):
    __tablename__ = "visitor_count"
    visitor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    member_id = db.Column(db.String(20), index=True)
    member_name = db.Column(db.String(255), nullable=False)
    institution = db.Column(db.String(100))
    checkin_date = db.Column(db.DateTime, nullable=False)


class SystemLog(db.Model):
    __tablename__ = "system_log"
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    log_type = db.Column(db.Enum("staff", "member", "system"), nullable=False, default="staff")
    id = db.Column(db.String(50))
    log_location = db.Column(db.String(50), nullable=False)
    sub_module = db.Column(db.String(50))
    action = db.Column(db.String(50))
    log_msg = db.Column(db.Text, nullable=False)
    log_date = db.Column(db.DateTime, nullable=False)


class Setting(db.Model):
    __tablename__ = "setting"
    setting_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    setting_name = db.Column(db.String(30), nullable=False, unique=True)
    setting_value = db.Column(db.Text)


class Content(db.Model):
    __tablename__ = "content"
    content_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content_title = db.Column(db.String(255), nullable=False)
    content_desc = db.Column(db.Text, nullable=False)
    content_path = db.Column(db.String(20), nullable=False, unique=True)
    is_news = db.Column(db.SmallInteger)
    input_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)


class Comment(db.Model):
    __tablename__ = "comment"
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    biblio_id = db.Column(db.Integer, nullable=False, index=True)
    member_id = db.Column(db.String(20), nullable=False, index=True)
    comment = db.Column(db.Text, nullable=False)
    input_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_update = db.Column(db.DateTime, onupdate=datetime.utcnow)


class SearchBiblio(db.Model):
    __tablename__ = "search_biblio"
    biblio_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    author = db.Column(db.Text)
    topic = db.Column(db.Text)
    publisher = db.Column(db.String(100))
    publish_year = db.Column(db.String(20))
    call_number = db.Column(db.String(50))


class Files(db.Model):
    __tablename__ = "files"
    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    file_title = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.Text, nullable=False)
    mime_type = db.Column(db.String(100))
    uploader_id = db.Column(db.Integer, nullable=False)
    input_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)


class Plugins(db.Model):
    __tablename__ = "plugins"
    id = db.Column(db.String(32), primary_key=True)
    options = db.Column(db.JSON)
    path = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    uid = db.Column(db.Integer, nullable=False)


class BackupLog(db.Model):
    __tablename__ = "backup_log"
    backup_log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False, default=0)
    backup_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    backup_file = db.Column(db.Text)


class BiblioView(db.Model):
    __tablename__ = "biblio_view"
    biblio_id = db.Column(db.Integer, primary_key=True)
    views = db.Column(db.Integer, nullable=False, default=0)
    last_viewed = db.Column(db.DateTime)
