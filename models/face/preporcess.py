import tensorflow as tf

def data_process(train_data_path, val_data_path, batch_size):
    # 훈련 데이터셋 생성
    train_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        train_data_path,
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=True
    )

    # 검증 데이터셋 생성
    val_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        val_data_path,
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=False
    )

    # 표준화 (Normalization) 추가
    # 입력 이미지의 평균과 표준편차를 사용하여 데이터 표준화
    standardization_layer = tf.keras.layers.Rescaling(1./255)  # 이미지를 0-1 범위로 표준화
    train_dataset = train_dataset.map(lambda x, y: (standardization_layer(x), y))
    val_dataset = val_dataset.map(lambda x, y: (standardization_layer(x), y))

    # 데이터 증강 (augmentation) 추가: 훈련 데이터에 여러가지 변형을 추가
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),   # 랜덤 좌우 반전
        tf.keras.layers.RandomRotation(0.2),        # 랜덤 회전
        tf.keras.layers.RandomZoom(0.1),            # 랜덤 확대/축소
        tf.keras.layers.RandomContrast(0.2),        # 랜덤 대비 변화
        tf.keras.layers.RandomBrightness(0.2)       # 랜덤 밝기 변화
    ])

    # 훈련 데이터에 데이터 증강을 적용
    train_dataset = train_dataset.map(lambda x, y: (data_augmentation(x, training=True), y))

    # 검증 데이터에는 증강을 적용하지 않음
    # 검증 데이터는 오직 표준화만 진행
    # val_dataset = val_dataset.map(lambda x, y: (standardization_layer(x), y))

    return train_dataset, val_dataset
