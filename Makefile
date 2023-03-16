export FLASK_APP:=flask/app.py

.PHONY: all
all: build push

.PHONY: build
build:
	docker build -t neotel/microtoken-${TARGET}:${TAG} ${TARGET}/

.PHONY: push
push:
	docker push neotel/microtoken-${TARGET}:${TAG}

.PHONY: dev
dev:
ifeq ($(TARGET),fastapi)
	uvicorn --app-dir fastapi main:app --reload
else ifeq ($(TARGET),flask)
	flask run --debug
else
	@echo Error: $(TARGET) not implemented.
endif

