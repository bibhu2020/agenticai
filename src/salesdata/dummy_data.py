"""
dummy_data.py — Complete Microsoft Northwind Database Seeder

Creates and populates the standard 11-table Northwind schema in PostgreSQL.
Based on the original Microsoft Northwind Traders sample database.
"""

import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

np.random.seed(42)

DB_URL = "postgresql://neondb_owner:npg_h4FkSJfs9taC@ep-young-brook-a8mnh7la-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require"
engine = create_engine(DB_URL)


def setup_schema():
    """Create the complete Northwind schema (11 tables)."""
    print("🔧 Creating complete Northwind schema...")
    with engine.connect() as conn:
        # Drop in reverse dependency order
        for t in [
            "employee_territories", "order_details", "orders",
            "products", "territories", "regions",
            "customers", "employees", "shippers",
            "suppliers", "categories"
        ]:
            conn.execute(text(f"DROP TABLE IF EXISTS {t} CASCADE"))
        conn.commit()

        ddl = """
        -- 1. Categories
        CREATE TABLE categories (
            category_id SMALLINT PRIMARY KEY,
            category_name VARCHAR(50) NOT NULL,
            description TEXT
        );

        -- 2. Suppliers
        CREATE TABLE suppliers (
            supplier_id SMALLINT PRIMARY KEY,
            company_name VARCHAR(80) NOT NULL,
            contact_name VARCHAR(60),
            contact_title VARCHAR(60),
            address VARCHAR(120),
            city VARCHAR(30),
            region VARCHAR(30),
            postal_code VARCHAR(20),
            country VARCHAR(30),
            phone VARCHAR(30),
            fax VARCHAR(30)
        );

        -- 3. Products
        CREATE TABLE products (
            product_id SMALLINT PRIMARY KEY,
            product_name VARCHAR(80) NOT NULL,
            supplier_id SMALLINT REFERENCES suppliers(supplier_id),
            category_id SMALLINT REFERENCES categories(category_id),
            quantity_per_unit VARCHAR(40),
            unit_price NUMERIC(10,2),
            units_in_stock SMALLINT DEFAULT 0,
            units_on_order SMALLINT DEFAULT 0,
            reorder_level SMALLINT DEFAULT 0,
            discontinued SMALLINT DEFAULT 0,
            product_manual TEXT
        );

        -- 4. Customers
        CREATE TABLE customers (
            customer_id VARCHAR(10) PRIMARY KEY,
            company_name VARCHAR(80) NOT NULL,
            contact_name VARCHAR(60),
            contact_title VARCHAR(60),
            address VARCHAR(120),
            city VARCHAR(30),
            region VARCHAR(30),
            postal_code VARCHAR(20),
            country VARCHAR(30),
            phone VARCHAR(30),
            fax VARCHAR(30),
            type VARCHAR(20)
        );

        -- 5. Employees
        CREATE TABLE employees (
            employee_id SMALLINT PRIMARY KEY,
            last_name VARCHAR(40) NOT NULL,
            first_name VARCHAR(20) NOT NULL,
            title VARCHAR(60),
            title_of_courtesy VARCHAR(10),
            birth_date DATE,
            hire_date DATE,
            address VARCHAR(120),
            city VARCHAR(30),
            region VARCHAR(30),
            postal_code VARCHAR(20),
            country VARCHAR(30),
            home_phone VARCHAR(30),
            extension VARCHAR(10),
            notes TEXT,
            reports_to SMALLINT REFERENCES employees(employee_id)
        );

        -- 6. Shippers
        CREATE TABLE shippers (
            shipper_id SMALLINT PRIMARY KEY,
            company_name VARCHAR(80) NOT NULL,
            phone VARCHAR(30)
        );

        -- 7. Orders
        CREATE TABLE orders (
            order_id SMALLINT PRIMARY KEY,
            customer_id VARCHAR(10) REFERENCES customers(customer_id),
            employee_id SMALLINT REFERENCES employees(employee_id),
            order_date DATE,
            required_date DATE,
            shipped_date DATE,
            ship_via SMALLINT REFERENCES shippers(shipper_id),
            freight NUMERIC(10,2),
            ship_name VARCHAR(80),
            ship_address VARCHAR(120),
            ship_city VARCHAR(30),
            ship_region VARCHAR(30),
            ship_postal_code VARCHAR(20),
            ship_country VARCHAR(30)
        );

        -- 8. Order Details
        CREATE TABLE order_details (
            order_id SMALLINT REFERENCES orders(order_id),
            product_id SMALLINT REFERENCES products(product_id),
            unit_price NUMERIC(10,2) NOT NULL,
            quantity SMALLINT NOT NULL,
            discount REAL DEFAULT 0,
            PRIMARY KEY (order_id, product_id)
        );

        -- 9. Regions
        CREATE TABLE regions (
            region_id SMALLINT PRIMARY KEY,
            region_description VARCHAR(100) NOT NULL
        );

        -- 10. Territories
        CREATE TABLE territories (
            territory_id VARCHAR(20) PRIMARY KEY,
            territory_description VARCHAR(100) NOT NULL,
            region_id SMALLINT REFERENCES regions(region_id)
        );

        -- 11. Employee Territories
        CREATE TABLE employee_territories (
            employee_id SMALLINT REFERENCES employees(employee_id),
            territory_id VARCHAR(20) REFERENCES territories(territory_id),
            PRIMARY KEY (employee_id, territory_id)
        );
        """
        conn.execute(text(ddl))
        conn.commit()
    print("✅ Schema created (11 tables)")


def seed_data():
    """Populate with standard Northwind data."""
    print("📦 Seeding Northwind data...")
    with engine.connect() as conn:

        # ── Categories (8 standard) ──
        conn.execute(text("""
        INSERT INTO categories (category_id, category_name, description) VALUES
        (1, 'Beverages', 'Soft drinks, coffees, teas, beers, and ales'),
        (2, 'Condiments', 'Sweet and savory sauces, relishes, spreads, and seasonings'),
        (3, 'Confections', 'Desserts, candies, and sweet breads'),
        (4, 'Dairy Products', 'Cheeses'),
        (5, 'Grains/Cereals', 'Breads, crackers, pasta, and cereal'),
        (6, 'Meat/Poultry', 'Prepared meats'),
        (7, 'Produce', 'Dried fruit and bean curd'),
        (8, 'Seafood', 'Seaweed and fish')
        """))

        # ── Suppliers (29 standard) ──
        suppliers = [
            (1,'Exotic Liquids','Charlotte Cooper','Purchasing Manager','49 Gilbert St.','London',None,'EC1 4SD','UK','(171) 555-2222',None),
            (2,'New Orleans Cajun Delights','Shelley Burke','Order Administrator','P.O. Box 78934','New Orleans','LA','70117','USA','(100) 555-4822',None),
            (3,'Grandma Kelly''s Homestead','Regina Murphy','Sales Representative','707 Oxford Rd.','Ann Arbor','MI','48104','USA','(313) 555-5735','(313) 555-3349'),
            (4,'Tokyo Traders','Yoshi Nagase','Marketing Manager','9-8 Sekimai Musashino-shi','Tokyo',None,'100','Japan','(03) 3555-5011',None),
            (5,'Cooperativa de Quesos Las Cabras','Antonio del Valle Saavedra','Export Administrator','Calle del Rosal 4','Oviedo','Asturias','33007','Spain','(98) 598 76 54',None),
            (6,'Mayumi''s','Mayumi Ohno','Marketing Representative','92 Setsuko Chuo-ku','Osaka',None,'545','Japan','(06) 431-7877',None),
            (7,'Pavlova Ltd.','Ian Devling','Marketing Manager','74 Rose St. Moonie Ponds','Melbourne','Victoria','3058','Australia','(03) 444-2343','(03) 444-6588'),
            (8,'Specialty Biscuits Ltd.','Peter Wilson','Sales Representative','29 King''s Way','Manchester',None,'M14 GSD','UK','(161) 555-4448',None),
            (9,'PB Knackebrod AB','Lars Peterson','Sales Agent','Kaloadagatan 13','Goteborg',None,'S-345 67','Sweden','031-987 65 43','031-987 65 91'),
            (10,'Refrescos Americanas LTDA','Carlos Diaz','Marketing Manager','Av. das Americanas 12.890','Sao Paulo',None,'5442','Brazil','(11) 555 4640',None),
            (11,'Heli Susswaren GmbH & Co. KG','Petra Winkler','Sales Manager','Tiergartenstrasse 5','Berlin',None,'10785','Germany','(010) 9984510',None),
            (12,'Plutzer Lebensmittelgrossmarkte AG','Martin Bein','International Marketing Mgr.','Bogenallee 51','Frankfurt',None,'60439','Germany','(069) 992755',None),
            (13,'Nord-Ost-Fisch Handelsgesellschaft mbH','Sven Petersen','Coordinator Foreign Markets','Frahmredder 112a','Cuxhaven',None,'27478','Germany','(04721) 8713','(04721) 8714'),
            (14,'Formaggi Fortini s.r.l.','Elio Rossi','Sales Representative','Viale Dante 75','Ravenna',None,'48100','Italy','(0544) 60323','(0544) 60603'),
            (15,'Norske Meierier','Beate Vileid','Marketing Manager','Hatlevegen 5','Sandvika',None,'1320','Norway','(0)2-953010',None),
            (16,'Bigfoot Breweries','Cheryl Saylor','Regional Account Rep.','3400 - 8th Avenue Suite 210','Bend','OR','97101','USA','(503) 555-9931',None),
            (17,'Svensk Sjofoda AB','Michael Bjorn','Sales Representative','Brovallavagen 231','Stockholm',None,'S-123 45','Sweden','08-123 45 67',None),
            (18,'Aux joyeux ecclesiastiques','Guylene Nodier','Sales Manager','203, Rue des Francs-Bourgeois','Paris',None,'75004','France','(1) 03.83.00.68','(1) 03.83.00.62'),
            (19,'New England Seafood Cannery','Robb Merchant','Wholesale Account Agent','Order Processing Dept.','Boston','MA','02134','USA','(617) 555-3267','(617) 555-3389'),
            (20,'Leka Trading','Chandra Leka','Owner','471 Serangoon Loop Suite 402','Singapore',None,'0512','Singapore','555-8787',None),
            (21,'Lyngbysild','Niels Petersen','Sales Manager','Lyngbysild Fiskebakken 10','Lyngby',None,'2800','Denmark','43844108','43844115'),
            (22,'Zaanse Snoepfabriek','Dirk Luchte','Accounting Manager','Verkoop Ransen 9','Zaandam',None,'9999 ZZ','Netherlands','(12345) 1212','(12345) 1210'),
            (23,'Karkki Oy','Anne Heikkonen','Product Manager','Valtakatu 12','Lappeenranta',None,'53120','Finland','(953) 10956',None),
            (24,'G''day Mate','Wendy Mackenzie','Sales Representative','170 Prince Edward Parade','Sydney','NSW','2042','Australia','(02) 555-5914','(02) 555-4873'),
            (25,'Ma Maison','Jean-Guy Lauzon','Marketing Manager','2960 Rue St. Laurent','Montreal','Quebec','H1J 1C3','Canada','(514) 555-9022',None),
            (26,'Pasta Buttini s.r.l.','Giovanni Giudici','Order Administrator','Via dei Gelsomini 153','Salerno',None,'84100','Italy','(089) 6547665','(089) 6547667'),
            (27,'Escargots Nouveaux','Marie Delamare','Sales Manager','22, rue H. Voiron','Montceau',None,'71300','France','85.57.00.07',None),
            (28,'Gai paturage','Eliane Noz','Sales Representative','Bat. B 3, rue des Alpes','Annecy',None,'74000','France','38.76.98.06','38.76.98.58'),
            (29,'Forets d''erables','Chantal Goulet','Accounting Manager','148 rue Chasseur','Ste-Hyacinthe','Quebec','J2S 7S8','Canada','(514) 555-2955','(514) 555-2921')
        ]
        for s in suppliers:
            conn.execute(text("""
                INSERT INTO suppliers (supplier_id,company_name,contact_name,contact_title,address,city,region,postal_code,country,phone,fax)
                VALUES (:sid,:cn,:ctn,:ct,:addr,:city,:reg,:pc,:co,:ph,:fx)
            """), {"sid":s[0],"cn":s[1],"ctn":s[2],"ct":s[3],"addr":s[4],"city":s[5],"reg":s[6],"pc":s[7],"co":s[8],"ph":s[9],"fx":s[10]})

        # ── Products (77 standard Northwind products) ──
        products = [
            (1,'Chai',1,1,'10 boxes x 20 bags',18.00,39,0,10,0),
            (2,'Chang',1,1,'24 - 12 oz bottles',19.00,17,40,25,0),
            (3,'Aniseed Syrup',1,2,'12 - 550 ml bottles',10.00,13,70,25,0),
            (4,'Chef Anton''s Cajun Seasoning',2,2,'48 - 6 oz jars',22.00,53,0,0,0),
            (5,'Chef Anton''s Gumbo Mix',2,2,'36 boxes',21.35,0,0,0,1),
            (6,'Grandma''s Boysenberry Spread',3,2,'12 - 8 oz jars',25.00,120,0,25,0),
            (7,'Uncle Bob''s Organic Dried Pears',3,7,'12 - 1 lb pkgs.',30.00,15,0,10,0),
            (8,'Northwoods Cranberry Sauce',3,2,'12 - 12 oz jars',40.00,6,0,0,0),
            (9,'Mishi Kobe Niku',4,6,'18 - 500 g pkgs.',97.00,29,0,0,1),
            (10,'Ikura',4,8,'12 - 200 ml jars',31.00,31,0,0,0),
            (11,'Queso Cabrales',5,4,'1 kg pkg.',21.00,22,30,30,0),
            (12,'Queso Manchego La Pastora',5,4,'10 - 500 g pkgs.',38.00,86,0,0,0),
            (13,'Konbu',6,8,'2 kg box',6.00,24,0,5,0),
            (14,'Tofu',6,7,'40 - 100 g pkgs.',23.25,35,0,0,0),
            (15,'Genen Shouyu',6,2,'24 - 250 ml bottles',15.50,39,0,5,0),
            (16,'Pavlova',7,3,'32 - 500 g boxes',17.45,29,0,10,0),
            (17,'Alice Mutton',7,6,'20 - 1 kg tins',39.00,0,0,0,1),
            (18,'Carnarvon Tigers',7,8,'16 kg pkg.',62.50,42,0,0,0),
            (19,'Teatime Chocolate Biscuits',8,3,'10 boxes x 12 pieces',9.20,25,0,5,0),
            (20,'Sir Rodney''s Marmalade',8,3,'30 gift boxes',81.00,40,0,0,0),
            (21,'Sir Rodney''s Scones',8,3,'24 pkgs. x 4 pieces',10.00,3,40,5,0),
            (22,'Gustaf''s Knackebrod',9,5,'24 - 500 g pkgs.',21.00,104,0,25,0),
            (23,'Tunnbrod',9,5,'12 - 250 g pkgs.',9.00,61,0,25,0),
            (24,'Guarana Fantastica',10,1,'12 - 355 ml cans',4.50,20,0,0,1),
            (25,'NuNuCa Nuss-Nougat-Creme',11,3,'20 - 450 g glasses',14.00,76,0,30,0),
            (26,'Gumbar Gummibarchen',11,3,'100 - 250 g bags',31.23,15,0,0,0),
            (27,'Schoggi Schokolade',11,3,'100 - 100 g pieces',43.90,49,0,30,0),
            (28,'Rossle Sauerkraut',12,7,'25 - 825 g cans',45.60,26,0,0,1),
            (29,'Thuringer Rostbratwurst',12,6,'50 bags x 30 sausgs.',123.79,0,0,0,1),
            (30,'Nord-Ost Matjeshering',13,8,'10 - 200 g glasses',25.89,10,0,15,0),
            (31,'Gorgonzola Telino',14,4,'12 - 100 g pkgs',12.50,0,70,20,0),
            (32,'Mascarpone Fabioli',14,4,'24 - 200 g pkgs.',32.00,9,40,25,0),
            (33,'Geitost',15,4,'500 g',2.50,112,0,20,0),
            (34,'Sasquatch Ale',16,1,'24 - 12 oz bottles',14.00,111,0,15,0),
            (35,'Steeleye Stout',16,1,'24 - 12 oz bottles',18.00,20,0,15,0),
            (36,'Inlagd Sill',17,8,'24 - 250 g jars',19.00,112,0,20,0),
            (37,'Gravad lax',17,8,'12 - 500 g pkgs.',26.00,11,50,25,0),
            (38,'Cote de Blaye',18,1,'12 - 75 cl bottles',263.50,17,0,15,0),
            (39,'Chartreuse verte',18,1,'750 cc per bottle',18.00,69,0,5,0),
            (40,'Boston Crab Meat',19,8,'24 - 4 oz tins',18.40,123,0,30,0),
            (41,'Jack''s New England Clam Chowder',19,8,'12 - 12 oz cans',9.65,85,0,10,0),
            (42,'Singaporean Hokkien Fried Mee',20,5,'32 - 1 kg pkgs.',14.00,26,0,0,1),
            (43,'Ipoh Coffee',20,1,'16 - 500 g tins',46.00,17,10,25,0),
            (44,'Gula Malacca',20,2,'20 - 2 kg bags',19.45,27,0,15,0),
            (45,'Rogede sild',21,8,'1k pkg.',9.50,5,70,15,0),
            (46,'Spegesild',21,8,'4 - 450 g glasses',12.00,95,0,0,0),
            (47,'Zaanse koeken',22,3,'10 - 4 oz boxes',9.50,36,0,0,0),
            (48,'Chocolade',22,3,'10 pkgs.',12.75,15,70,25,0),
            (49,'Maxilaku',23,3,'24 - 50 g pkgs.',20.00,10,60,15,0),
            (50,'Valkoinen suklaa',23,3,'12 - 100 g bars',16.25,65,0,30,0),
            (51,'Manjimup Dried Apples',24,7,'50 - 300 g pkgs.',53.00,20,0,10,0),
            (52,'Filo Mix',24,5,'16 - 2 kg boxes',7.00,38,0,25,0),
            (53,'Perth Pasties',24,6,'48 pieces',32.80,0,0,0,1),
            (54,'Tourtiere',25,6,'16 pies',7.45,21,0,10,0),
            (55,'Pate chinois',25,6,'24 boxes x 2 pies',24.00,115,0,20,0),
            (56,'Gnocchi di nonna Alice',26,5,'24 - 250 g pkgs.',38.00,21,10,30,0),
            (57,'Ravioli Angelo',26,5,'24 - 250 g pkgs.',19.50,36,0,20,0),
            (58,'Escargots de Bourgogne',27,8,'24 pieces',13.25,62,0,20,0),
            (59,'Raclette Courdavault',28,4,'5 kg pkg.',55.00,79,0,0,0),
            (60,'Camembert Pierrot',28,4,'15 - 300 g rounds',34.00,19,0,0,0),
            (61,'Sirop d''erable',29,2,'24 - 500 ml bottles',28.50,113,0,25,0),
            (62,'Tarte au sucre',29,3,'48 pies',49.30,17,0,0,0),
            (63,'Vegie-spread',7,2,'15 - 625 g jars',43.90,24,0,5,0),
            (64,'Wimmers gute Semmelknodel',12,5,'20 bags x 4 pieces',33.25,22,80,30,0),
            (65,'Louisiana Fiery Hot Pepper Sauce',2,2,'32 - 8 oz bottles',21.05,76,0,0,0),
            (66,'Louisiana Hot Spiced Okra',2,2,'24 - 8 oz jars',17.00,4,100,20,0),
            (67,'Laughing Lumberjack Lager',16,1,'24 - 12 oz bottles',14.00,52,0,10,0),
            (68,'Scottish Longbreads',8,3,'10 boxes x 8 pieces',12.50,6,10,15,0),
            (69,'Gudbrandsdalsost',15,4,'10 kg pkg.',36.00,26,0,15,0),
            (70,'Outback Lager',7,1,'24 - 355 ml bottles',15.00,15,10,30,0),
            (71,'Flotemysost',15,4,'10 - 500 g pkgs.',21.50,26,0,0,0),
            (72,'Mozzarella di Giovanni',14,4,'24 - 200 g pkgs.',34.80,14,0,0,0),
            (73,'Rod Kaviar',17,8,'24 - 150 g jars',15.00,101,0,5,0),
            (74,'Longlife Tofu',4,7,'5 kg pkg.',10.00,4,20,5,0),
            (75,'Rhonbrau Klosterbier',12,1,'24 - 0.5 l bottles',7.75,125,0,25,0),
            (76,'Lakkalikoori',23,1,'500 ml',18.00,57,0,20,0),
            (77,'Original Frankfurter grune Sosse',12,2,'12 boxes',13.00,32,0,15,0)
        ]
        for p in products:
            p_manual = f"Official manual for {p[1]}. This high-quality product is designed for professional use in the {p[3]} category. Please handle with care and refer to local regulations."
            conn.execute(text("""
                INSERT INTO products (product_id,product_name,supplier_id,category_id,quantity_per_unit,unit_price,units_in_stock,units_on_order,reorder_level,discontinued,product_manual)
                VALUES (:pid,:pn,:sid,:cid,:qpu,:up,:uis,:uoo,:rl,:disc,:pm)
            """), {"pid":p[0],"pn":p[1],"sid":p[2],"cid":p[3],"qpu":p[4],"up":p[5],"uis":p[6],"uoo":p[7],"rl":p[8],"disc":p[9],"pm":p_manual})

        # ── Shippers (3 standard) ──
        conn.execute(text("""
        INSERT INTO shippers (shipper_id, company_name, phone) VALUES
        (1, 'Speedy Express', '(503) 555-9831'),
        (2, 'United Package', '(503) 555-3199'),
        (3, 'Federal Shipping', '(503) 555-9931')
        """))

        # ── Employees (9 standard) ──
        conn.execute(text("""
        INSERT INTO employees (employee_id,last_name,first_name,title,title_of_courtesy,birth_date,hire_date,address,city,region,postal_code,country,home_phone,extension,notes,reports_to) VALUES
        (1,'Davolio','Nancy','Sales Representative','Ms.','1968-12-08','1992-05-01','507 - 20th Ave. E.','Seattle','WA','98122','USA','(206) 555-9857','5467','Education includes a BA in psychology.',NULL),
        (2,'Fuller','Andrew','Vice President Sales','Dr.','1952-02-19','1992-08-14','908 W. Capital Way','Tacoma','WA','98401','USA','(206) 555-9482','3457','Has an MBA from university.',NULL)
        """))
        conn.execute(text("""
        INSERT INTO employees (employee_id,last_name,first_name,title,title_of_courtesy,birth_date,hire_date,address,city,region,postal_code,country,home_phone,extension,notes,reports_to) VALUES
        (3,'Leverling','Janet','Sales Representative','Ms.','1963-08-30','1992-04-01','722 Moss Bay Blvd.','Kirkland','WA','98033','USA','(206) 555-3412','3355','Has a BS degree in chemistry.',2),
        (4,'Peacock','Margaret','Sales Representative','Mrs.','1958-09-19','1993-05-03','4110 Old Redmond Rd.','Redmond','WA','98052','USA','(206) 555-8122','5176','Member of Toastmasters International.',2),
        (5,'Buchanan','Steven','Sales Manager','Mr.','1955-03-04','1993-10-17','14 Garrett Hill','London',NULL,'SW1 8JR','UK','(71) 555-4848','3453','Has a BSc degree.',2),
        (6,'Suyama','Michael','Sales Representative','Mr.','1963-07-02','1993-10-17','Coventry House','London',NULL,'EC2 7JR','UK','(71) 555-7773','428','EFL in college.',5),
        (7,'King','Robert','Sales Representative','Mr.','1960-05-29','1994-01-02','Edgeham Hollow','London',NULL,'RG1 9SP','UK','(71) 555-5598','465','BA degree in English from St. Lawrence College.',5),
        (8,'Callahan','Laura','Inside Sales Coordinator','Ms.','1958-01-09','1994-03-05','4726 - 11th Ave. N.E.','Seattle','WA','98105','USA','(206) 555-1189','2344','BA in psychology.',2),
        (9,'Dodsworth','Anne','Sales Representative','Ms.','1969-07-02','1994-11-15','7 Houndstooth Rd.','London',NULL,'WG2 7LT','UK','(71) 555-4444','452','Has a BA degree in English.',5)
        """))

        # ── Regions (4 standard) ──
        conn.execute(text("""
        INSERT INTO regions (region_id, region_description) VALUES
        (1, 'Eastern'), (2, 'Western'), (3, 'Northern'), (4, 'Southern')
        """))

        # ── Territories (sample) ──
        territories = [
            ('01581','Westboro',1),('01730','Bedford',1),('01833','Georgetow',1),
            ('02116','Boston',1),('02139','Cambridge',1),('02184','Braintree',1),
            ('06897','Wilton',1),('07960','Morristown',1),('08837','Edison',1),
            ('10019','New York',1),('10038','New York',1),('27403','Greensboro',1),
            ('27511','Cary',1),('29202','Columbia',4),('30346','Atlanta',4),
            ('31406','Savannah',4),('32859','Orlando',4),('33607','Tampa',4),
            ('40222','Louisville',1),('44122','Beachwood',3),('45839','Findlay',3),
            ('48075','Southfield',3),('48084','Troy',3),('55113','Roseville',3),
            ('55439','Minneapolis',3),('60179','Hoffman Estates',2),('60601','Chicago',2),
            ('72716','Bentonville',4),('75234','Dallas',4),('78759','Austin',4),
            ('80202','Denver',2),('80909','Colorado Springs',2),('85014','Phoenix',2),
            ('85251','Scottsdale',2),('90405','Santa Monica',2),('94025','Menlo Park',2),
            ('94105','San Francisco',2),('95008','Campbell',2),('95054','Santa Clara',2),
            ('95060','Santa Cruz',2),('98004','Bellevue',2),('98052','Redmond',2),
            ('98104','Seattle',2)
        ]
        for t in territories:
            conn.execute(text("INSERT INTO territories (territory_id,territory_description,region_id) VALUES (:tid,:td,:rid)"),
                         {"tid":t[0],"td":t[1],"rid":t[2]})

        # ── Employee Territories ──
        et = [
            (1,'06897'),(1,'19713'),(2,'01581'),(2,'01730'),(2,'01833'),(2,'02116'),(2,'02139'),(2,'02184'),(2,'40222'),
            (3,'30346'),(3,'31406'),(3,'32859'),(3,'33607'),(4,'20852'),(4,'27403'),(4,'27511'),
            (5,'07960'),(5,'10019'),(5,'10038'),(5,'29202'),
            (6,'48075'),(6,'48084'),(6,'44122'),
            (7,'60601'),(7,'60179'),(7,'80202'),(7,'80909'),(7,'55113'),(7,'55439'),
            (8,'98004'),(8,'98052'),(8,'98104'),
            (9,'75234'),(9,'78759'),(9,'72716')
        ]
        # Only insert territories that exist
        existing = set(t[0] for t in territories)
        for e in et:
            if e[1] in existing:
                conn.execute(text("INSERT INTO employee_territories (employee_id,territory_id) VALUES (:eid,:tid)"),
                             {"eid":e[0],"tid":e[1]})

        # ── Customers (91 standard Northwind customers) ──
        customers = [
            ('ALFKI','Alfreds Futterkiste','Maria Anders','Sales Representative','Obere Str. 57','Berlin',None,'12209','Germany','030-0074321','030-0076545'),
            ('ANATR','Ana Trujillo Emparedados y helados','Ana Trujillo','Owner','Avda. de la Constitucion 2222','Mexico D.F.',None,'05021','Mexico','(5) 555-4729','(5) 555-3745'),
            ('ANTON','Antonio Moreno Taqueria','Antonio Moreno','Owner','Mataderos 2312','Mexico D.F.',None,'05023','Mexico','(5) 555-3932',None),
            ('AROUT','Around the Horn','Thomas Hardy','Sales Representative','120 Hanover Sq.','London',None,'WA1 1DP','UK','(171) 555-7788','(171) 555-6750'),
            ('BERGS','Berglunds snabbkop','Christina Berglund','Order Administrator','Berguvsvagen 8','Lulea',None,'S-958 22','Sweden','0921-12 34 65','0921-12 34 67'),
            ('BLAUS','Blauer See Delikatessen','Hanna Moos','Sales Representative','Forsterstr. 57','Mannheim',None,'68306','Germany','0621-08460','0621-08924'),
            ('BLONP','Blondel pere et fils','Frederique Citeaux','Marketing Manager','24, place Kleber','Strasbourg',None,'67000','France','88.60.15.31','88.60.15.32'),
            ('BOLID','Bolido Comidas preparadas','Martin Sommer','Owner','C/ Araquil 67','Madrid',None,'28023','Spain','(91) 555 22 82','(91) 555 91 99'),
            ('BONAP','Bon app''','Laurence Lebihan','Owner','12, rue des Bouchers','Marseille',None,'13008','France','91.24.45.40','91.24.45.41'),
            ('BOTTM','Bottom-Dollar Markets','Elizabeth Lincoln','Accounting Manager','23 Tsawassen Blvd.','Tsawassen','BC','T2F 8M4','Canada','(604) 555-4729','(604) 555-3745'),
            ('BSBEV','B''s Beverages','Victoria Ashworth','Sales Representative','Fauntleroy Circus','London',None,'EC2 5NT','UK','(171) 555-1212',None),
            ('CACTU','Cactus Comidas para llevar','Patricio Simpson','Sales Agent','Cerrito 333','Buenos Aires',None,'1010','Argentina','(1) 135-5555','(1) 135-4892'),
            ('CENTC','Centro comercial Moctezuma','Francisco Chang','Marketing Manager','Sierras de Granada 9993','Mexico D.F.',None,'05022','Mexico','(5) 555-3392','(5) 555-7293'),
            ('CHOPS','Chop-suey Chinese','Yang Wang','Owner','Hauptstr. 29','Bern',None,'3012','Switzerland','0452-076545',None),
            ('COMMI','Comercio Mineiro','Pedro Afonso','Sales Associate','Av. dos Lusiadas 23','Sao Paulo','SP','05432-043','Brazil','(11) 555-7647',None),
            ('CONSH','Consolidated Holdings','Elizabeth Brown','Sales Representative','Berkeley Gardens 12','London',None,'WX1 6LT','UK','(171) 555-2282','(171) 555-9199'),
            ('DRACD','Drachenblut Delikatessen','Sven Ottlieb','Order Administrator','Walserweg 21','Aachen',None,'52066','Germany','0241-039123','0241-059428'),
            ('DUMON','Du monde entier','Janine Labrune','Owner','67, rue des Cinquante Otages','Nantes',None,'44000','France','40.67.88.88','40.67.89.89'),
            ('EASTC','Eastern Connection','Ann Devon','Sales Agent','35 King George','London',None,'WX3 6FW','UK','(171) 555-0297','(171) 555-3373'),
            ('ERNSH','Ernst Handel','Roland Mendel','Sales Manager','Kirchgasse 6','Graz',None,'8010','Austria','7675-3425','7675-3426'),
            ('FAMIA','Familia Arquibaldo','Aria Cruz','Marketing Assistant','Rua Oros 92','Sao Paulo','SP','05442-030','Brazil','(11) 555-9857',None),
            ('FISSA','FISSA Fabrica Inter. Salchichas S.A.','Diego Roel','Accounting Manager','C/ Moralzarzal 86','Madrid',None,'28034','Spain','(91) 555 94 44','(91) 555 55 93'),
            ('FOLIG','Folies gourmandes','Martine Rance','Assistant Sales Agent','184, chaussee de Tournai','Lille',None,'59000','France','20.16.10.16','20.16.10.17'),
            ('FOLKO','Folk och fa HB','Maria Larsson','Owner','Akergatan 24','Bracke',None,'S-844 67','Sweden','0695-34 67 21',None),
            ('FRANK','Frankenversand','Peter Franken','Marketing Manager','Berliner Platz 43','Munchen',None,'80805','Germany','089-0877310','089-0877451'),
            ('FRANR','France restauration','Carine Schmitt','Marketing Manager','54, rue Royale','Nantes',None,'44000','France','40.32.21.21','40.32.21.20'),
            ('FRANS','Franchi S.p.A.','Paolo Accorti','Sales Representative','Via Monte Bianco 34','Torino',None,'10100','Italy','011-4988260','011-4988261'),
            ('FURIB','Furia Bacalhau e Frutos do Mar','Lino Rodriguez','Sales Manager','Jardim das rosas n. 32','Lisboa',None,'1675','Portugal','(1) 354-2534','(1) 354-2535'),
            ('GALED','Galeria del gastronomo','Eduardo Saavedra','Marketing Manager','Rambla de Cataluna 23','Barcelona',None,'08022','Spain','(93) 203 4560','(93) 203 4561'),
            ('GODOS','Godos Cocina Tipica','Jose Pedro Freyre','Sales Manager','C/ Romero 33','Sevilla',None,'41101','Spain','(95) 555 82 82',None),
            ('GOURL','Gourmet Lanchonetes','Andre Fonseca','Sales Associate','Av. Brasil 442','Campinas','SP','04876-786','Brazil','(11) 555-9482',None),
            ('GREAL','Great Lakes Food Market','Howard Snyder','Marketing Manager','2732 Baker Blvd.','Eugene','OR','97403','USA','(503) 555-7555',None),
            ('GROSR','GROSELLA-Restaurante','Manuel Pereira','Owner','5th Ave. #422','Rio de Janeiro','RJ','05432-043','Brazil','(21) 555-7272','(21) 555-7272'),
            ('HANAR','Hanari Carnes','Mario Pontes','Accounting Manager','Rua do Paco 67','Rio de Janeiro','RJ','05454-876','Brazil','(21) 555-0091','(21) 555-8765'),
            ('HILAA','HILARION-Abastos','Carlos Hernandez','Sales Representative','Carrera 22 con Ave. Carlos Soublette #8-35','San Cristobal','Tachira','5022','Venezuela','(5) 555-1340','(5) 555-1948'),
            ('HUNGC','Hungry Coyote Import Store','Yoshi Latimer','Sales Representative','City Center Plaza 516 Main St.','Elgin','OR','97827','USA','(503) 555-6874','(503) 555-2376'),
            ('HUNGO','Hungry Owl All-Night Grocers','Patricia McKenna','Sales Associate','8 Johnstown Road','Cork',None,None,'Ireland','2967 542','2967 3333'),
            ('ISLAT','Island Trading','Helen Bennett','Marketing Manager','Garden House Crowther Way','Cowes',None,'PO31 7PJ','UK','(198) 555-8888',None),
            ('KOENE','Koniglich Essen','Philip Cramer','Sales Associate','Maubelstr. 90','Brandenburg',None,'14776','Germany','0555-09876',None),
            ('LACOR','La corne d''abondance','Daniel Tonini','Sales Representative','67, avenue de l''Europe','Versailles',None,'78000','France','30.59.84.10','30.59.85.11'),
            ('LAMAI','La maison d''Asie','Annette Roulet','Sales Manager','1 rue Alsace-Lorraine','Toulouse',None,'31000','France','61.77.61.10','61.77.61.11'),
            ('LAUGB','Laughing Bacchus Wine Cellars','Yoshi Tannamuri','Marketing Assistant','1900 Oak St.','Vancouver','BC','V3F 2K1','Canada','(604) 555-3392','(604) 555-7293'),
            ('LAZYK','Lazy K Kountry Store','John Steel','Marketing Manager','12 Orchestra Terrace','Walla Walla','WA','99362','USA','(509) 555-7969','(509) 555-6221'),
            ('LEHMS','Lehmanns Marktstand','Renate Messner','Sales Representative','Magazinweg 7','Frankfurt a.M.',None,'60528','Germany','069-0245984','069-0245874'),
            ('LETSS','Let''s Stop N Shop','Jaime Yorres','Owner','87 Polk St. Suite 5','San Francisco','CA','94117','USA','(415) 555-5938',None),
            ('LILAS','LILA-Supermercado','Carlos Gonzalez','Accounting Manager','Carrera 52 con Ave. Bolivar #65-98 Llano Largo','Barquisimeto','Lara','3508','Venezuela','(9) 331-6954','(9) 331-7256'),
            ('LINOD','LINO-Delicateses','Felipe Izquierdo','Owner','Ave. 5 de Mayo Porlamar','I. de Margarita','Nueva Esparta','4980','Venezuela','(8) 34-56-12','(8) 34-93-93'),
            ('LONEP','Lonesome Pine Restaurant','Fran Wilson','Sales Manager','89 Chiaroscuro Rd.','Portland','OR','97219','USA','(503) 555-9573','(503) 555-9646'),
            ('MAGAA','Magazzini Alimentari Riuniti','Giovanni Rovelli','Marketing Manager','Via Ludovico il Moro 22','Bergamo',None,'24100','Italy','035-640230','035-640231'),
            ('MAISD','Maison Dewey','Catherine Dewey','Sales Agent','Rue Joseph-Bens 532','Bruxelles',None,'B-1180','Belgium','(02) 201 24 67','(02) 201 24 68'),
            ('MEREP','Mere Paillarde','Jean Fresniere','Marketing Assistant','43 rue St. Laurent','Montreal','Quebec','H1J 1C3','Canada','(514) 555-8054','(514) 555-8055'),
            ('MORGK','Morgenstern Gesundkost','Alexander Feuer','Marketing Assistant','Heerstr. 22','Leipzig',None,'04179','Germany','0342-023176',None),
            ('NORTS','North/South','Simon Crowther','Sales Associate','South House 300 Queensbridge','London',None,'SW7 1RZ','UK','(171) 555-7733','(171) 555-2530'),
            ('OCEAN','Oceano Atlantico Ltda.','Yvonne Moncada','Sales Agent','Ing. Gustavo Moncada 8585','Buenos Aires',None,'1010','Argentina','(1) 135-5333','(1) 135-5535'),
            ('OLDWO','Old World Delicatessen','Rene Phillips','Sales Representative','2743 Bering St.','Anchorage','AK','99508','USA','(907) 555-7584','(907) 555-2880'),
            ('OTTIK','Ottilies Kaseladen','Henriette Pfalzheim','Owner','Mehrheimerstr. 369','Koln',None,'50739','Germany','0221-0644327','0221-0765721'),
            ('PARIS','Paris specialites','Marie Bertrand','Owner','265, boulevard Charonne','Paris',None,'75012','France','(1) 42.34.22.66','(1) 42.34.22.77'),
            ('PERIC','Pericles Comidas clasicas','Guillermo Fernandez','Sales Representative','Calle Dr. Jorge Cash 321','Mexico D.F.',None,'05033','Mexico','(5) 552-3745','(5) 545-3745'),
            ('PICCO','Piccolo und mehr','Georg Pipps','Sales Manager','Geislweg 14','Salzburg',None,'5020','Austria','6562-9722','6562-9723'),
            ('PRINI','Princesa Isabel Vinhos','Isabel de Castro','Sales Representative','Estrada da saude n. 58','Lisboa',None,'1756','Portugal','(1) 356-5634',None),
            ('QUEDE','Que Delicia','Bernardo Batista','Accounting Manager','Rua da Panificadora 12','Rio de Janeiro','RJ','02389-673','Brazil','(21) 555-4252','(21) 555-4545'),
            ('QUEEN','Queen Cozinha','Lucia Carvalho','Marketing Assistant','Alameda dos Canarios 891','Sao Paulo','SP','05487-020','Brazil','(11) 555-1189',None),
            ('QUICK','QUICK-Stop','Horst Kloss','Accounting Manager','Taucherstrasse 10','Cunewalde',None,'01307','Germany','0372-035188',None),
            ('RANCH','Rancho grande','Sergio Gutierrez','Sales Representative','Av. del Libertador 900','Buenos Aires',None,'1010','Argentina','(1) 123-5555','(1) 123-5556'),
            ('RATTC','Rattlesnake Canyon Grocery','Paula Wilson','Assistant Sales Representative','2817 Milton Dr.','Albuquerque','NM','87110','USA','(505) 555-5939','(505) 555-3620'),
            ('REGGC','Reggiani Caseifici','Maurizio Moroni','Sales Associate','Strada Provinciale 124','Reggio Emilia',None,'42100','Italy','0522-556721','0522-556722'),
            ('RICAR','Ricardo Adocicados','Janete Limeira','Assistant Sales Agent','Av. Copacabana 267','Rio de Janeiro','RJ','02389-890','Brazil','(21) 555-3412',None),
            ('RICSU','Richter Supermarkt','Michael Holz','Sales Manager','Grenzacherweg 237','Geneve',None,'1203','Switzerland','0897-034214',None),
            ('ROMEY','Romero y tomillo','Alejandra Camino','Accounting Manager','Gran Via 1','Madrid',None,'28001','Spain','(91) 745 6200','(91) 745 6210'),
            ('SANTG','Sante Gourmet','Jonas Bergulfsen','Owner','Erling Skakkes gate 78','Stavern',None,'4110','Norway','07-98 92 35','07-98 92 47'),
            ('SAVEA','Save-a-lot Markets','Jose Pavarotti','Sales Representative','187 Suffolk Ln.','Boise','ID','83720','USA','(208) 555-8097',None),
            ('SEVES','Seven Seas Imports','Hari Kumar','Sales Manager','90 Wadhurst Rd.','London',None,'OX15 4NB','UK','(171) 555-1717','(171) 555-5646'),
            ('SIMOB','Simons bistro','Jytte Petersen','Owner','Vinbaeltet 34','Kobenhavn',None,'1734','Denmark','31 12 34 56','31 13 35 57'),
            ('SPECD','Specialites du monde','Dominique Perrier','Marketing Manager','25, rue Lauriston','Paris',None,'75016','France','(1) 47.55.60.10','(1) 47.55.60.20'),
            ('SPLIR','Split Rail Beer & Ale','Art Braunschweiger','Sales Manager','P.O. Box 555','Lander','WY','82520','USA','(307) 555-4680','(307) 555-6525'),
            ('SUPRD','Supremes delices','Pascale Cartrain','Accounting Manager','Boulevard Tirou 255','Charleroi',None,'B-6000','Belgium','(071) 23 67 22 20','(071) 23 67 22 21'),
            ('THEBI','The Big Cheese','Liz Nixon','Marketing Manager','89 Jefferson Way Suite 2','Portland','OR','97201','USA','(503) 555-3612',None),
            ('THECR','The Cracker Box','Liu Wong','Marketing Assistant','55 Grizzly Peak Rd.','Butte','MT','59801','USA','(406) 555-5834','(406) 555-8083'),
            ('TOMSP','Toms Spezialitaten','Karin Josephs','Marketing Manager','Luisenstr. 48','Munster',None,'44087','Germany','0251-031259','0251-035695'),
            ('TORTU','Tortuga Restaurante','Miguel Angel Paolino','Owner','Avda. Azteca 123','Mexico D.F.',None,'05033','Mexico','(5) 555-2933',None),
            ('TRADH','Tradicao Hipermercados','Anabela Domingues','Sales Representative','Av. Ines de Castro 414','Sao Paulo','SP','05634-030','Brazil','(11) 555-2167','(11) 555-2168'),
            ('TRAIH','Trail''s Head Gourmet Provisioners','Helvetius Nagy','Sales Associate','722 DaVinci Blvd.','Kirkland','WA','98034','USA','(206) 555-8257','(206) 555-2174'),
            ('VAFFE','Vaffeljernet','Palle Ibsen','Sales Manager','Smagsloget 45','Arhus',None,'8200','Denmark','86 21 32 43','86 22 33 44'),
            ('VICTE','Victuailles en stock','Mary Saveley','Sales Agent','2, rue du Commerce','Lyon',None,'69004','France','78.32.54.86','78.32.54.87'),
            ('VINET','Vins et alcools Chevalier','Paul Henriot','Accounting Manager','59 rue de l''Abbaye','Reims',None,'51100','France','26.47.15.10','26.47.15.11'),
            ('WANDK','Die Wandernde Kuh','Rita Muller','Sales Representative','Adenauerallee 900','Stuttgart',None,'70563','Germany','0711-020361','0711-035428'),
            ('WARTH','Wartian Herkku','Pirkko Koskitalo','Accounting Manager','Torikatu 38','Oulu',None,'90110','Finland','981-443655','981-443655'),
            ('WELLI','Wellington Importadora','Paula Parente','Sales Manager','Rua do Mercado 12','Resende','SP','08737-363','Brazil','(14) 555-8122',None),
            ('WHITC','White Clover Markets','Karl Jablonski','Owner','305 - 14th Ave. S. Suite 3B','Seattle','WA','98128','USA','(206) 555-4112','(206) 555-4115'),
            ('WILMK','Wilman Kala','Matti Karttunen','Owner/Marketing Assistant','Keskuskatu 45','Helsinki',None,'21240','Finland','90-224 8858','90-224 8858'),
            ('WOLZA','Wolski  Zajazd','Zbyszek Piestrzeniewicz','Owner','ul. Filtrowa 68','Warszawa',None,'01-012','Poland','(26) 642-7012','(26) 642-7012')
        ]
        types = ['Enterprise', 'SME', 'Government']
        for c in customers:
            ctype = np.random.choice(types)
            conn.execute(text("""
                INSERT INTO customers (customer_id,company_name,contact_name,contact_title,address,city,region,postal_code,country,phone,fax,type)
                VALUES (:cid,:cn,:ctn,:ct,:addr,:city,:reg,:pc,:co,:ph,:fx,:type)
            """), {"cid":c[0],"cn":c[1],"ctn":c[2],"ct":c[3],"addr":c[4],"city":c[5],"reg":c[6],"pc":c[7],"co":c[8],"ph":c[9],"fx":c[10],"type":ctype})

        # ── Orders & Order Details (~200 orders) ──
        print("  Generating 1000 orders with line items...")
        cust_ids = [c[0] for c in customers]
        emp_ids = list(range(1, 10))
        ship_ids = [1, 2, 3]
        prod_prices = {p[0]: p[5] for p in products}
        active_products = [p[0] for p in products if p[9] == 0]

        orders_batch = []
        details_batch = []
        order_id = 10248  # Standard Northwind starting order ID
        
        import time
        start_time = time.time()

        for i in range(1000):
            cid = str(np.random.choice(cust_ids))
            eid = int(np.random.choice(emp_ids))
            sid = int(np.random.choice(ship_ids))

            # Spread orders across 2004 till today (2026)
            order_date = datetime(2004, 1, 1) + timedelta(days=int(np.random.randint(0, 8100)))
            req_date = order_date + timedelta(days=int(np.random.randint(7, 30)))
            ship_date = order_date + timedelta(days=int(np.random.randint(1, 20))) if np.random.random() > 0.05 else None
            freight = round(float(np.random.uniform(1.0, 350.0)), 2)

            # Get customer info for ship fields
            cust_row = next(c for c in customers if c[0] == cid)

            orders_batch.append({
                "oid": order_id, "cid": cid, "eid": eid,
                "od": order_date.date(), "rd": req_date.date(),
                "sd": ship_date.date() if ship_date else None,
                "sv": sid, "fr": freight,
                "sn": cust_row[1], "sa": cust_row[4], "sc": cust_row[5],
                "sr": cust_row[6], "spc": cust_row[7], "sco": cust_row[8]
            })

            # 1-5 line items per order
            num_items = int(np.random.randint(1, 6))
            order_products = np.random.choice(active_products, size=min(num_items, len(active_products)), replace=False)
            for pid in order_products:
                qty = int(np.random.randint(1, 50))
                price = float(prod_prices[int(pid)])
                disc = float(np.random.choice([0.0, 0.0, 0.0, 0.05, 0.10, 0.15, 0.20, 0.25]))
                details_batch.append({"oid": order_id, "pid": int(pid), "up": price, "qty": qty, "disc": disc})

            order_id += 1

            # Progress feedback
            if (i+1) % 50 == 0:
                print(f"  ...prepared {i+1} orders")

        # Perform batch insertions
        print(f"  🚀 Inserting {len(orders_batch)} orders...")
        conn.execute(text("""
            INSERT INTO orders (order_id,customer_id,employee_id,order_date,required_date,shipped_date,
                ship_via,freight,ship_name,ship_address,ship_city,ship_region,ship_postal_code,ship_country)
            VALUES (:oid,:cid,:eid,:od,:rd,:sd,:sv,:fr,:sn,:sa,:sc,:sr,:spc,:sco)
        """), orders_batch)

        print(f"  🚀 Inserting {len(details_batch)} line items...")
        conn.execute(text("""
            INSERT INTO order_details (order_id,product_id,unit_price,quantity,discount)
            VALUES (:oid,:pid,:up,:qty,:disc)
        """), details_batch)

        conn.commit()
        elapsed = time.time() - start_time
        print(f"  ✨ Bulk seeding completed in {elapsed:.2f} seconds.")

    # Count results
    with engine.connect() as conn:
        for table in ['categories','suppliers','products','customers','employees','shippers','orders','order_details','regions','territories','employee_territories']:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  ✅ {table}: {count} rows")

    print("\n🎉 Northwind database fully populated!")


if __name__ == "__main__":
    setup_schema()
    seed_data()