DO $$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'hotel_user') THEN
    CREATE USER hotel_user WITH ENCRYPTED PASSWORD 'hotel_pass';
  END IF;
END $$;
GRANT ALL PRIVILEGES ON DATABASE hotel TO hotel_user;
