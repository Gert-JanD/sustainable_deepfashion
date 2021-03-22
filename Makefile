CATEGORY_ID = 1
MIN_PAIR_COUNT = 10
INSTRUCTION =
DEEPFASHION_DATA = merged

setup-data: setup-deepfashion-train-data setup-deepfashion-validation-data merge-database preprocess

setup-deepfashion-train-data: DEEPFASHION_DATA = train
setup-deepfashion-train-data: download-df-train extract-df-train database-df-train

setup-deepfashion-validation-data: DEEPFASHION_DATA = validation
setup-deepfashion-validation-data: download-df-validation extract-df-validation database-df-validation

setup-gc: connect-google-drive setup-deepfashion-train-data-gc setup-deepfashion-validation-data-gc

setup-deepfashion-train-data-gc: DEEPFASHION_DATA = train
setup-deepfashion-train-data-gc: download-df-train-gc extract-df-train database-df-train

setup-deepfashion-validation-data-gc: DEEPFASHION_DATA = validation
setup-deepfashion-validation-data-gc: download-df-validation-gc extract-df-validation database-df-validation

download-df-train download-df-validation:
	mkdir -p data/raw
	python -m src.data.setup_data --data="$(DEEPFASHION_DATA)"

download-df-train-gc download-df-validaiton-gc:
	ln -sfn /gdrive/MyDrive/DeepFashion2\ Dataset/$(DEEPFASHHION_DATA).zip data/raw/

extract-df-train extract-df-validation:
	mkdir -p data/intermediate
	unzip -n -d data/intermediate/ data/raw/$(DEEPFASHION_DATA).zip

extract-df-train-gc extract-df-validation-gc:
	mkdir -p data/intermediate
	chmod a+x scripts/google_colab_utility/unzip_data.sh
	scripts/google_colab_utility/unzip_data.sh $(DEEPFASHION_DATA)

database-df-train database-df-validation:
	mkdir -p data/processed
	python -m src.data.write_deepfashion2_database --input="$(shell pwd)/data/intermediate/$(DEEPFASHION_DATA)" --output="data/processed/deepfashion_$(DEEPFASHION_DATA).joblib"

merge-database:
	mkdir -p data/processed
	python -m src.data.merge_databases --inputs "$(shell pwd)/data/processed/deepfashion_train.joblib" "$(shell pwd)/data/processed/deepfashion_validation.joblib" --output "$(shell pwd)/data/processed/deepfashion_merged.joblib"

preprocess: DEEPFASHION_DATA = merged
preprocess:
	python -m src.data.preprocess_data --input="data/processed/deepfashion_$(DEEPFASHION_DATA).joblib" --output="$(shell pwd)/data/processed/category_$(CATEGORY_ID)_min_count_$(MIN_PAIR_COUNT)/" --category=$(CATEGORY_ID) --min_count=$(MIN_PAIR_COUNT)

clean-unprocessed:
	rm -r data/raw data/intermediate

connect-google-drive:
	python -m src.google_colab_utility connect_gdrive

save-preprocessed-gc:
	mkdir -p /gdrive/MyDrive/deepfashion_gc_save
	zip -r /gdrive/MyDrive/deepfashion_gc_save/preprocessed_cat_$(CATEGORY_ID)_min_count_$(MIN_PAIR_COUNT).zip data/processed/category_$(CATEGORY_ID)_min_count_$(MIN_PAIR_COUNT) data/processed/category_id_$(CATEGORY_ID)_min_pair_count_$(MIN_PAIR_COUNT)_deepfashion_train.joblib data/processed/category_id_$(CATEGORY_ID)_min_pair_count_$(MIN_PAIR_COUNT)_deepfashion_validation.joblib

setup-preprocessed-gc:
	python -m src.google_colab_utility connect_gdrive
	unzip /gdrive/MyDrive/deepfashion_gc_save/preprocessed_cat_$(CATEGORY_ID)_min_count_$(MIN_PAIR_COUNT).zip

train-aws-stop:
	python -m src.train_from_instruction --instruction=$(INSTRUCTION)
	sudo shutdown now -h

train:
	python -m src.train_from_instruction --instruction=$(INSTRUCTION)
