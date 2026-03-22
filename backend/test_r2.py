from app.services.storage.factory import get_storage_service

storage = get_storage_service()

result = storage.save_file(
    data=b"hello r2",
    relative_path="test/hello.txt",
)

print(result)