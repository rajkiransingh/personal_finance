# personal_finance
creating an application for tracking individual personal finances

# Setting Up the Environment Variables

To configure the application, you need to provide the necessary database credentials and other sensitive information through a .env file. This file stores environment variables securely and is required for the application to function correctly.

Steps to Create a .env File
Create a .env File in the Project Root Directory

Navigate to the root directory of the project.

Create a new file named .env.

Example command:

bash

touch .env

Add the Following Variables to the .env File Copy and paste the following lines into your .env file and replace the placeholder values with your actual credentials:

makefile
Copy code
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=your_database_name
MYSQL_USER=your_database_user
MYSQL_PASSWORD=your_user_password
Example:

makefile
Copy code
MYSQL_ROOT_PASSWORD=password123
MYSQL_DATABASE=personal_finance_db
MYSQL_USER=finance_user
MYSQL_PASSWORD=secure_password
Save the .env File

Ensure the file is saved in the root directory of the project.
Do not share or commit this file to version control (e.g., Git). It contains sensitive information.
Verify the .env File

Before running the application, ensure the .env file is correctly configured and in the right location.
Important Notes:
The .env file is used to provide secure, configurable access to database credentials and other secrets.
Ensure this file is never shared or uploaded to public repositories.
Add .env to the .gitignore file to prevent it from being tracked by Git.