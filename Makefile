default:
	cd flashcard_app && docker run -d -p 5000:5000 -v ./../my_flashcard_data:/data --name flashcard-instance flashcard-app

build:
	cd flashcard_app && docker build -t flashcard-app .

down:
	docker stop flashcard-instance
	docker rm flashcard-instance
