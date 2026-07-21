import uvicorn

if __name__ == "__main__":
    print(" Запуск сервера Finlite DB...")
    print(" API доступно по адресу: http://127.0.0.1:8000")

    uvicorn.run(
        "presentationSQL:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )