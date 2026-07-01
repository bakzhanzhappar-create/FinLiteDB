import uvicorn

if __name__ == "__main__":
    print(" Запуск сервера Finlite DB...")
    print(" API доступно по адресу: http://127.0.0.1:8000")

    # Запускаем приложение из модуля presentation
    uvicorn.run(
        "presentation:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )