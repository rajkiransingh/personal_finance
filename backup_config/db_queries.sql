-- ################################################ CREATE TABLES ################################################

-- Creating the needed tables for the project
-- Creating the user table
CREATE TABLE users (
	user_id INT AUTO_INCREMENT PRIMARY KEY, 
	name VARCHAR(255) NOT NULL
);


-- Creating table for units
CREATE TABLE units (
    unit_id INT AUTO_INCREMENT PRIMARY KEY,
    unit_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE transaction_types (
    transaction_type_id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_name VARCHAR(50) NOT NULL UNIQUE
);


-- Creating Income, Expense and Investment categories
CREATE TABLE income_source (
	income_source_id INT AUTO_INCREMENT PRIMARY KEY, 
	name VARCHAR(255) NOT NULL, description VARCHAR(255)
);

CREATE TABLE expense_category (
	expense_category_id INT AUTO_INCREMENT PRIMARY KEY, 
	name VARCHAR(255) NOT NULL, description VARCHAR(255)
);

CREATE TABLE investment_category (	
	id INT AUTO_INCREMENT PRIMARY KEY, 
	investment_type VARCHAR(100) NOT NULL, 	
	UNIQUE KEY unique_investment_type (investment_type)
);

CREATE TABLE investment_subcategory (
	id INT AUTO_INCREMENT PRIMARY KEY, 
	investment_subcategory_name VARCHAR(50) NOT NULL, 
	category_id INT, 
	FOREIGN KEY (category_id) REFERENCES investment_category(id)
);


-- Creating currency table for investment / expenses
CREATE TABLE currencies (
	currency_id INT PRIMARY KEY AUTO_INCREMENT,
	currency_code CHAR(3) NOT NULL,
	currency_name VARCHAR(50) NOT NULL,
	UNIQUE KEY unique_currencies (currency_code)
);

CREATE TABLE currency_conversion (
	id INT AUTO_INCREMENT PRIMARY KEY,
	from_currency_id INT,
	to_currency_id INT,
	conversion_rate DECIMAL(10,2) NOT NULL,
	last_updated DATE,
 	FOREIGN KEY (from_currency_id) REFERENCES currencies (currency_id),
	FOREIGN KEY (to_currency_id) REFERENCES currencies (currency_id)
);


-- Creating region
CREATE TABLE regions (
	region_id INT PRIMARY KEY AUTO_INCREMENT,
	region_name VARCHAR(50) NOT NULL,
	currency_id INT NOT NULL,
	FOREIGN KEY (currency_id) REFERENCES currencies (currency_id)
);


-- Creating Summary table for monthly data
CREATE TABLE monthly_financial_data (
	id INT AUTO_INCREMENT PRIMARY KEY,
	month INT NOT NULL,
	year INT NOT NULL,
	total_income DECIMAL(10,2),
	total_expenditure DECIMAL(10,2),
	investment_type VARCHAR(50),
	investment_amount DECIMAL(10,2),
	net_worth DECIMAL(10,2),
	UNIQUE KEY unique_month_year (month, year)
);

CREATE TABLE stock_holdings_summary (
    stock_name VARCHAR(50) NOT NULL,
    total_quantity DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,
    average_price_per_unit DECIMAL(10,2) NOT NULL,
    current_price_per_unit DECIMAL(10,2),
    investor_id INTEGER NOT NULL REFERENCES users(user_id),
    PRIMARY KEY (stock_name, investor_id)
);

CREATE TABLE mutual_fund_holdings_summary (
    mutual_fund_name VARCHAR(50) NOT NULL,
    total_quantity DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,
    average_price_per_unit DECIMAL(10,2) NOT NULL,
    current_price_per_unit DECIMAL(10,2),
    investor_id INTEGER NOT NULL REFERENCES users(user_id),
    PRIMARY KEY (mutual_fund_name, investor_id)
);


-- Creating investment data table
CREATE TABLE investment(
	id INT AUTO_INCREMENT PRIMARY KEY,
	investment_type_id INT,
	investment_subcategory_id INT,
	investment_name VARCHAR(10),
	investment_amount DECIMAL(10,2) NOT NULL,
	purchased_quantity DECIMAL(10,2) NOT NULL,
	unit_id INT NOT NULL,
	investor INT,
	FOREIGN KEY (investor) REFERENCES users(user_id),
	investment_date DATE NOT NULL,
	region_id INT,
	currency_id INT,
	initial_value DECIMAL(10,2),
	current_value DECIMAL(10,2),
	return_on_investment DECIMAL(10,2),
	FOREIGN KEY (region_id) REFERENCES regions(region_id),
	FOREIGN KEY (currency_id) REFERENCES currencies(currency_id),
	FOREIGN KEY (investment_type_id) REFERENCES investment_category(id),
	FOREIGN KEY (investment_subcategory_id) REFERENCES investment_subcategory(id),
	FOREIGN KEY (unit_id) REFERENCES units(unit_id)
);

-- Creating Assets and Liabilities
CREATE TABLE assets (
	asset_id INT AUTO_INCREMENT PRIMARY KEY,
	asset_type VARCHAR(255)
);

CREATE TABLE asset_subcategory (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	asset_id INT NOT NULL,
	FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE asset_value (
	id INT AUTO_INCREMENT PRIMARY KEY,
	asset_id INT NOT NULL,
	date DATE,
	value DECIMAL(10,2),
	FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

CREATE TABLE liabilities (
	liability_id INT AUTO_INCREMENT PRIMARY KEY,
	liability_type VARCHAR(255)
);

CREATE TABLE liability_subcategory (
	id INT AUTO_INCREMENT PRIMARY KEY,
	name VARCHAR(255) NOT NULL,
	liability_id INT NOT NULL,
	FOREIGN KEY (liability_id) REFERENCES liabilities(liability_id)
);

CREATE TABLE liability_value (
	id INT AUTO_INCREMENT PRIMARY KEY,
	liability_id INT NOT NULL,
	date DATE,
	value DECIMAL(10,2),
	FOREIGN KEY (liability_id) REFERENCES liabilities(liability_id)
);


-- Creating tables to enter income and expenses data
CREATE TABLE income (
	user_id INT,
	FOREIGN KEY (user_id) REFERENCES users (user_id),
	source_id INT NOT NULL, 
	FOREIGN KEY (source_id) REFERENCES income_source(income_source_id),
	amount FLOAT NOT NULL,
	currency VARCHAR(255) NOT NULL,
	earned_date DATE
);

CREATE TABLE expense (
	user_id INT,
	FOREIGN KEY (user_id) REFERENCES users (user_id),
	category_id INT NOT NULL, 
	FOREIGN KEY (category_id) REFERENCES expense_category(expense_category_id),
	amount FLOAT NOT NULL,
	currency VARCHAR(255) NOT NULL,
	spent_date DATE
);


-- Creating more tables to handle investments
-- Stock Transactions
CREATE TABLE stock_transactions (
	id INT AUTO_INCREMENT PRIMARY KEY,
	stock_name VARCHAR(255) NOT NULL,
	transaction_type_id INT NOT NULL,
	quantity DECIMAL(10,2) NOT NULL,
	price_per_unit DECIMAL(10,2) NOT NULL,
	transaction_date DATE NOT NULL,
	investor INT,
	FOREIGN KEY (investor) REFERENCES users(user_id),
	FOREIGN KEY (transaction_type_id) REFERENCES transaction_types(transaction_type_id)
);

-- Mutual Fund Transactions
CREATE TABLE mutual_fund_transactions (
	id INT AUTO_INCREMENT PRIMARY KEY,
	mutual_fund_name VARCHAR(255) NOT NULL,
	transaction_type_id INT NOT NULL,
	quantity DECIMAL(10,2) NOT NULL,
	price_per_unit DECIMAL(10,2) NOT NULL,
	transaction_date DATE NOT NULL,
	investor INT,
	FOREIGN KEY (investor) REFERENCES users(user_id),
	FOREIGN KEY (transaction_type_id) REFERENCES transaction_types(transaction_type_id)
);


CREATE TABLE audit_logs (
    audit_id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    record_id INT NOT NULL,  -- The ID of the record being modified
    operation_type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_data JSON,  -- Store old data in JSON format for updates and deletes
    new_data JSON,  -- Store new data in JSON format for inserts and updates
    changed_by INT,  -- The user who made the change
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Timestamp of the change
    FOREIGN KEY (changed_by) REFERENCES users(user_id)  -- Reference to the user table
);


DELIMITER //

CREATE TRIGGER log_user_insert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, record_id, operation_type, new_data, changed_by)
    VALUES ('users', NEW.user_id, 'INSERT', JSON_OBJECT('name', NEW.name), NEW.user_id);
END//


CREATE TRIGGER log_user_update
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, record_id, operation_type, old_data, new_data, changed_by)
    VALUES ('users', OLD.user_id, 'UPDATE', JSON_OBJECT('name', OLD.name), JSON_OBJECT('name', NEW.name), NEW.user_id);
END//


CREATE TRIGGER log_user_delete
AFTER DELETE ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (table_name, record_id, operation_type, old_data, changed_by)
    VALUES ('users', OLD.user_id, 'DELETE', JSON_OBJECT('name', OLD.name), OLD.user_id);
END//

DELIMITER ;



-- ############################################################## INSERT BASE VALUES ##############################################################
INSERT INTO users (name)
VALUES
('User 1'),
('User 2');

-- Populate the units table
INSERT INTO units (unit_name) VALUES ('Grams'), ('Unit'), ('SqYrds');

-- Populate the transaction_types table
INSERT INTO transaction_types (transaction_name) VALUES ('BUY'), ('SELL');

-- Inserting data into income source table
INSERT INTO income_source (name, description)
VALUES
('Salary', 'Monthly fixed salary from the company'),
('Bank Interest', 'Interest earned from bank every quarter'),
('Personal Interest', 'Interest earned from lending money to personals'),
('Dividends','Dividends from stocks'),
('Mutual Fund Returns', 'Money earned after redeeming the MFs'),
('Loan Return', 'Principle amount received back'),
('Policy Returns', 'Money received from the policies created for investments');

-- Inserting data into expense categories table
INSERT INTO expense_category (name, description)
VALUES
('Administrative Expenses', 'Expenses occured when dealing with government paperwork'),
('Bank Fees', 'Expenses occured for maintaining the bank account, deducted as part of bank fees every month / quarter'),
('Bills', 'Various bill payments like Electricity, water, mobile etc.,'),
('Clothing', 'Expenses for buying clothes'),
('Entertainment', 'Some expenses occured as part of recreational actitivities with family'),
('Food', 'Expenses occured as part of buying food from outside'),
('Fuel', 'Buying fuel for motor vehicle'),
('Gift','Expenses for buying gifts'),
('Health', 'Expenses occured on health issues'),
('Home', 'Money sent to Home'),
('Loan Repayment', 'Money used to repay existing loans'),
('Misc', 'Miscelleneous expenses which cannot be put into a category'),
('Money Transfer', 'Money transferred to indian accounts'),
('Rent', 'Rental expenses'),
('School Fees', 'Kids school fees'),
('Shopping', 'Groceries or other shopping expenses'),
('Transport', 'Transportation expenses for tram / taxi / bus');

-- Inserting data into currencies table
INSERT INTO currencies (currency_code , currency_name)
VALUES
('INR', 'Indian Rupee'),
('PLN', 'Polish Zloty'),
('USD', 'US Dollar');

-- Inserting data into the regions table
INSERT INTO regions (region_name, currency_id)
VALUES
('India', (SELECT currency_id FROM currencies WHERE currency_code = 'INR')),
('Poland', (SELECT currency_id FROM currencies WHERE currency_code = 'PLN')),
('USA', (SELECT currency_id FROM currencies WHERE currency_code = 'USD'));


INSERT INTO investment_category (investment_type)
VALUES
('Bullion'),
('Indian Stock'),
('Land'),
('LIC'),
('Mutual Fund'),
('Other Policies'),
('Sukanya Samriddhi Account'),
('US Stocks');


INSERT INTO investment_subcategory (investment_subcategory_name, category_id)
VALUES
('Gold', (SELECT id FROM investment_category WHERE investment_type = 'Bullion')),
('Silver', (SELECT id FROM investment_category WHERE investment_type = 'Bullion')),
('Plot', (SELECT id FROM investment_category WHERE investment_type = 'Land')),
('House', (SELECT id FROM investment_category WHERE investment_type = 'Land'));


-- Inserting standard categories in assets / liabilities
INSERT INTO assets (asset_type)
VALUES
('Investments'),
('Retirement'),
('Bullion'),
('Cash');

INSERT INTO asset_subcategory (name, asset_id)
VALUES
('Mutual Funds', (SELECT asset_id FROM assets WHERE asset_type = 'Investments')),
('Stocks', (SELECT asset_id FROM assets WHERE asset_type = 'Investments')),
('Interest Money', (SELECT asset_id FROM assets WHERE asset_type = 'Investments')),
('Land', (SELECT asset_id FROM assets WHERE asset_type = 'Investments')),
('Pension', (SELECT asset_id FROM assets WHERE asset_type = 'Retirement')),
('PF', (SELECT asset_id FROM assets WHERE asset_type = 'Retirement')),
('Gold', (SELECT asset_id FROM assets WHERE asset_type = 'Bullion')),
('Silver', (SELECT asset_id FROM assets WHERE asset_type = 'Bullion')),
('Cash in Hand', (SELECT asset_id FROM assets WHERE asset_type = 'Cash'));


INSERT INTO liabilities (liability_type)
VALUES
('Home Loan'),
('Personal Loan'),
('Hand Loan');


-- ############################################################## FETCH DATA ##############################################################
Select * FROM users;
Select * FROM income_source;
Select * FROM expense_category;
Select * FROM currencies;
Select * FROM regions;


Select * FROM assets;
Select * FROM liabilities;
Select * FROM asset_subcategory;
Select * FROM liability_subcategory;
Select * FROM investment_category;
Select * FROM investment_subcategory;


Select * FROM income;
Select * FROM expense;
Select * FROM investment;
