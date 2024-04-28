package repository

import (
	"database/sql"
	"fmt"

	_ "github.com/lib/pq"
)

func CreateDatabaseConnect(dbname string) (*sql.DB, error) {
	dbHost := "postgresql"   //os.Getenv("DB_HOST")
	dbPort := "5432"         //os.Getenv("DB_PORT")
	dbUser := "postgres"     //os.Getenv("DB_USER_NAME")
	dbPassword := "postgres" //os.Getenv("DB_PASSWORD")
	dbName := dbname         //os.Getenv("DB_NAME")
	//connectionString := fmt.Sprintf("postgres://%v:%v@%v:%v/%v?sslmode=disable",
	//	dbUser, dbPassword, dbHost, dbPort, dbName)
	dataSourceName := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		dbHost, dbPort, dbUser, dbPassword, dbName)
	//fmt.Println(connectionString)
	db, err := sql.Open("postgres", dataSourceName)
	return db, err
}
