import tensorflow as tf
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

def data_process(batch_size):
    # 경로 수정
    train_data_path = ''
    val_data_path = ''

    # 데이터셋 생성
    train_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        train_data_path,
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=True
    )
    val_dataset = tf.keras.preprocessing.image_dataset_from_directory(
        val_data_path,
        image_size=(224, 224),
        batch_size=batch_size,
        shuffle=False
    )

    # 표준화 (0-1 스케일)
    standardization_layer = tf.keras.layers.Rescaling(1./255)
    train_dataset = train_dataset.map(lambda x, y: (standardization_layer(x), y))
    val_dataset = val_dataset.map(lambda x, y: (standardization_layer(x), y))

    # 데이터 증강
    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip("horizontal"),
        tf.keras.layers.RandomRotation(0.2),
        tf.keras.layers.RandomZoom(0.1),
        tf.keras.layers.RandomContrast(0.2)
    ])

    train_dataset = train_dataset.map(lambda x, y: (data_augmentation(x, training=True), y))

    return train_dataset, val_dataset

def create_model(input_shape=(224, 224, 3), num_classes=4):
    base_model = tf.keras.applications.EfficientNetB2(
        weights='imagenet', include_top=False, input_shape=input_shape
    )
    base_model.trainable = True  # 사전 훈련된 모델의 가중치 동결 해제

    model = tf.keras.Sequential([
        base_model,
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(num_classes, activation='softmax')
    ])

    # 학습률 감소 적용
    optimizer = tf.keras.optimizers.Adam(learning_rate=0.0001)  

    model.compile(optimizer=optimizer, loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# 데이터셋 준비
batch_size = 32
train_dataset, val_dataset = data_process(batch_size)

# 모델 생성
model = create_model(input_shape=(224, 224, 3), num_classes=4)

# 콜백 설정 (EarlyStopping & ReduceLROnPlateau)
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True, verbose=1)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1, min_lr=1e-6)

# 모델 학습
model.fit(train_dataset, validation_data=val_dataset, epochs=20, callbacks=[early_stopping, reduce_lr])
