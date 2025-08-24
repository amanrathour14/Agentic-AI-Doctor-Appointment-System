#!/bin/bash

# MySQL Setup Script for MedAI Doctor Appointment System
# This script sets up MySQL database and user for the system

echo "🚀 Setting up MySQL for MedAI System..."

# Check if MySQL is running
if ! systemctl is-active --quiet mysql; then
    echo "📦 Starting MySQL service..."
    sudo systemctl start mysql
    sudo systemctl enable mysql
fi

# Set MySQL root password (change 'password' to your desired password)
MYSQL_ROOT_PASSWORD="password"
MYSQL_DB_NAME="doctor_appointments"
MYSQL_USER="medai_user"
MYSQL_USER_PASSWORD="medai_password"

echo "🔐 Setting up MySQL root password and database..."

# Create MySQL configuration file for non-interactive setup
sudo tee /tmp/mysql_secure_installation.sql > /dev/null <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$MYSQL_ROOT_PASSWORD';
FLUSH PRIVILEGES;
EOF

# Run MySQL secure installation
sudo mysql -u root < /tmp/mysql_secure_installation.sql

# Create database and user
sudo mysql -u root -p$MYSQL_ROOT_PASSWORD <<EOF
CREATE DATABASE IF NOT EXISTS $MYSQL_DB_NAME;
CREATE USER IF NOT EXISTS '$MYSQL_USER'@'localhost' IDENTIFIED BY '$MYSQL_USER_PASSWORD';
GRANT ALL PRIVILEGES ON $MYSQL_DB_NAME.* TO '$MYSQL_USER'@'localhost';
FLUSH PRIVILEGES;
SHOW DATABASES;
EOF

echo "✅ MySQL setup completed!"
echo "📋 Database: $MYSQL_DB_NAME"
echo "👤 User: $MYSQL_USER"
echo "🔑 Password: $MYSQL_USER_PASSWORD"
echo ""

# Update .env file with new credentials
if [ -f "../backend/.env" ]; then
    echo "🔄 Updating .env file with MySQL credentials..."
    sed -i "s|mysql://root:password@localhost/doctor_appointments|mysql://$MYSQL_USER:$MYSQL_USER_PASSWORD@localhost/$MYSQL_DB_NAME|g" "../backend/.env"
    echo "✅ .env file updated!"
else
    echo "⚠️  .env file not found. Please update manually:"
    echo "DATABASE_URL=mysql://$MYSQL_USER:$MYSQL_USER_PASSWORD@localhost/$MYSQL_DB_NAME"
fi

echo ""
echo "🚀 Next steps:"
echo "1. Run the MySQL schema: mysql -u $MYSQL_USER -p$MYSQL_USER_PASSWORD $MYSQL_DB_NAME < 01_create_database_schema_mysql.sql"
echo "2. Test the connection: python -c \"from database_models import get_session; print('Database connected!')\""
echo "3. Start your application!"