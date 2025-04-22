default:
	cd flashcard_app && podman run -d -p 5000:5000 -v ./../my_flashcard_data:/data --name flashcard-instance flashcard-app

build:
	cd flashcard_app && podman build -t flashcard-app .

down:
	podman stop flashcard-instance
	podman rm flashcard-instance
