import os
from idlelib import query

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, update
from telegram.ext import CallbackContext, CallbackQueryHandler
from moviepy.editor import VideoFileClip
import openai
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps, ImageEnhance
from moviepy.editor import *
from moviepy.editor import VideoFileClip, vfx
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
import logging
from telegram import KeyboardButton, ReplyKeyboardMarkup



# Установите свои ключи API для OpenAI и Telegram
openai.api_key = "YOUR_OPENAI_API_KEY"
telegram_bot_token = '6914516600:AAEJMgvwH-lm5rHsO2TLiY3KS_zplm3aWFw'




'''
    markup = types.ReplyKeyboardMarkup()
    generate_button = types.KeyboardButton('generate')
    filter_button = types.KeyboardButton('filter')
    crop_image_button = types.KeyboardButton('cropimage')
    crop_video_button = types.KeyboardButton('cropvideo')
    adjust_button = types.KeyboardButton('adjust')
    markup.row(generate_button, filter_button,crop_image_button, crop_video_button, adjust_button )
    # Создание клавиатуры с этими кнопками
    custom_keyboard = [[generate_button, filter_button], [crop_image_button, crop_video_button], [adjust_button]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
'''
# Функция для приветствия и описания команд
def start(update: Update, context: CallbackContext):


    start_text = """
Привет! Я бот Кузя и помогу тебе сгенерировать текста, наложить фильтр на изображение и обрезать изображение/видео.

Доступные команды:
/start - показать это сообщение
/generate <prompt> - сгенерировать текст на основе заданного prompt
/filter - наложить фильтр на изображение
/cropimage - обрезать изображение под предложенные размеры
/cropvideo - обрезать видео и наложить фильтр
/adjust - настроить яркость, экспозицию,контрастность
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_text)
    reply_keyboard = [['Сгенерировать текст', 'Пременить фильтр к фото'],
                          ['Обрезать изображение', 'Настроить пармметры фото '],
                          ['Обрезать видео', 'Наложить фильтр  на видео']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text('Выберите действие:', reply_markup=markup)


def function3(update, context):
    pass


def button_click(update, context):
    query = update.callback_query
    button = query.data
    if button == 'Сгенерировать текст':
        generate_text(update, context)
    elif button == 'Пременить фильтр к фото':
        function1(update, context)

    elif button == 'Кнопка 3':
        function3(update, context)
    elif button == 'Кнопка 4':
        function4(update, context)

def function1(update, context):
    update.message.reply_text('/filter')


# Создание кнопок

# Отправка клавиатуры пользователю
#update.reply_text('Выберите действие:', reply_markup=reply_markup)







# Функция для генерации текста
def generate_text(update: Update, context: CallbackContext):
    prompt = update.message.text.replace("/generate ", "")
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )
    generated_text = response.choices[0].text.strip()
    context.bot.send_message(chat_id=update.effective_chat.id, text=generated_text)
# Функция для обрезки изображения
def crop_image(update: Update, context: CallbackContext):
    context.user_data['last_command'] = '/cropimage'

    # Проверяем, что сообщение содержит фотографию
    if not update.message.photo:
        update.message.reply_text('Пожалуйста, отправьте фотографию для обрезки.')
        return

    # Получаем фотографию от пользователя
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('photo.jpg')

    # Создаем инлайн-кнопки для выбора формата
    keyboard = [[InlineKeyboardButton("9:16", callback_data='9:16'),
                 InlineKeyboardButton("4:5", callback_data='4:5')],
                [InlineKeyboardButton("1:1", callback_data='1:1'),
                 InlineKeyboardButton("16:9", callback_data='16:9')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с выбором формата в ответ на фотографию пользователя
    update.message.reply_photo(photo=open('photo.jpg', 'rb'), caption='Выберите формат обрезки:',
                               reply_markup=reply_markup)

    # Устанавливаем обработчик для выбора формата
    query_handler = CallbackQueryHandler(crop_chosen_format, pattern=r'9:16|4:5|1:1|16:9')
    context.dispatcher.add_handler(query_handler)

def crop_chosen_format(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data

    # Открываем фотографию с помощью Pillow
    image = Image.open('photo.jpg')

    # Получаем размер изображения
    width, height = image.size

    # Определяем размеры обрезанного изображения в зависимости от выбранного формата
    if callback_data == '9:16':
        new_width, new_height = int(height * 9 / 16), height
    elif callback_data == '4:5':
        new_width, new_height = int(height * 4 / 5), height
    elif callback_data == '1:1':
        new_width, new_height = min(width, height), min(width, height)
    elif callback_data == '16:9':
        new_width, new_height = width, int(width * 9 / 16)

    # Вычисляем координаты обрезки
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = (width + new_width) // 2
    bottom = (height + new_height) // 2

    # Обрезаем изображение
    cropped_image = image.crop((left, top, right, bottom))

    # Сохраняем обрезанное изображение
    cropped_image.save('cropped_photo.jpg')

    # Отправляем обрезанную фотографию пользователю
    with open('cropped_photo.jpg', 'rb') as photo_file:
        query.message.reply_photo(photo=photo_file)

    # Удаляем временные файлы
    os.remove('photo.jpg')
    os.remove('cropped_photo.jpg')

# Функция для наложения фильтра на фото
def aply_filter(update: Update, context: CallbackContext):
    context.user_data['last_command'] = '/filter'

    # Проверяем, что сообщение содержит фотографию
    if not update.message.photo:
        update.message.reply_text('Пожалуйста, отправьте фотографию для наложения фильтра в формате jpg.')
        return

    # Получаем фотографию от пользователя
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('photo.jpg')

    # Открываем фотографию с помощью Pillow
    image = Image.open('photo.jpg')

    # Создаем инлайн-кнопки для выбора фильтра
    keyboard = [[InlineKeyboardButton("Черно-белый", callback_data='grayscale'),
                 InlineKeyboardButton("Яркий", callback_data='bright')],
                [InlineKeyboardButton("Прохладный", callback_data='cool'),
                 InlineKeyboardButton("Эффектный", callback_data='vivid')],
                [InlineKeyboardButton("Теплый", callback_data='warm')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с выбором формата
    context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите фильтр:',
                             reply_markup=reply_markup)

    # Устанавливаем обработчик для выбора фильтра
    query_handler = CallbackQueryHandler(aply_chosen_filter, pattern=r'grayscale|bright|cool|vivid|warm')
    context.dispatcher.add_handler(query_handler)


# Функция для наложения выбранного фильтра
def aply_chosen_filter(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data

    # Открываем фотографию с помощью Pillow
    image = Image.open('photo.jpg')

    # Применяем фильтр к изображению
    filtered_image = apply_filter(image, callback_data)

    # Сохраняем отфильтрованное изображение
    filtered_image.save('filtered_photo.jpg')

    # Отправляем отфильтрованную фотографию пользователю
    with open('filtered_photo.jpg', 'rb') as photo_file:
        query.message.reply_photo(photo=photo_file)

    # Удаляем временные файлы
    os.remove('photo.jpg')
    os.remove('filtered_photo.jpg')

# Функция наложения фильтра
def apply_filter(image: Image.Image, filter_type: str) -> Image.Image:
    if filter_type == 'grayscale':
        return image.convert('L')
    elif filter_type == 'bright':
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1.5)
    elif filter_type == 'cool':
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(0.5)
    elif filter_type == 'vivid':
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1.5)
    elif filter_type == 'warm':
        enhancer = ImageEnhance.Warmth(image)
        return enhancer.enhance(1.5)




def adjust_image(update: Update, context: CallbackContext):
    context.user_data['last_command'] = '/adjust'

    # Проверяем, что сообщение содержит фотографию
    if not update.message.photo:
        update.message.reply_text('Пожалуйста, отправьте фотографию для настройки в формате jpg.')
        return

    # Получаем фотографию от пользователя
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('photo.jpg')

    # Создаем инлайн-кнопки для выбора параметра
    keyboard = [[InlineKeyboardButton("Яркость", callback_data='brightness'),
                 InlineKeyboardButton("Контрастность", callback_data='contrast')],
                [InlineKeyboardButton("Экспозиция", callback_data='sharpness')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с выбором параметра
    context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите параметр для настройки:',
                             reply_markup=reply_markup)

    # Устанавливаем обработчик для выбора параметра
    query_handler = CallbackQueryHandler(adjust_chosen_parameter, pattern=r'brightness|contrast|sharpness')
    context.dispatcher.add_handler(query_handler)


def adjust_chosen_parameter(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data

    # Открываем фотографию с помощью Pillow
    image = Image.open('photo.jpg')

    # Запрашиваем у пользователя значение параметра
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Выберите значение для {callback_data} от 1 до 10:")
    context.user_data['adjust_type'] = callback_data

    # Устанавливаем обработчик для получения значения параметра
    context.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command,
                                                  lambda update, context: get_adjust_value(update, context, image)))


def get_adjust_value(update: Update, context: CallbackContext, image: Image.Image):
    try:
        # Получаем значение параметра от пользователя
        value = int(update.message.text)

        # Проверяем, что значение в допустимом диапазоне
        if not 1 <= value <= 10:
            raise ValueError

        # Применяем настройку с учетом значения
        image = apply_adjustment(image, context.user_data['adjust_type'], value / 10)

        # Сохраняем обработанную фотографию
        image.save('adjusted_photo.jpg')
        image.close()

        # Отправляем обработанную фотографию пользователю
        with open('adjusted_photo.jpg', 'rb') as photo_file:
            context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_file)

        # Удаляем временные файлы
        os.remove('adjusted_photo.jpg')
        os.remove('photo.jpg')

        # Удаляем обработчик после получения значения параметра
        context.dispatcher.remove_handler(MessageHandler(Filters.text & ~Filters.command,
                                                  lambda update, context: get_adjust_value(update, context, image)))

    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Неверный формат значения. Введите число от 1 до 10.")


def apply_adjustment(image: Image.Image, adjust_type: str, value: float) -> Image.Image:
    if adjust_type == 'brightness':
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1 + (value*0.5))  # Увеличиваем яркость

    elif adjust_type == 'contrast':
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1 + (value*0.5))  # Увеличиваем контрастность

    elif adjust_type == 'sharpness':
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(1 + (value*1.5))  # Увеличиваем резкость

    return image  # Возвращаем исходное изображение, если параметр не найден



# Функция для обрезки видео
def cropvideo(update: Update, context: CallbackContext):
    context.user_data['last_command'] = '/cropvideo'

    # Проверяем, что сообщение содержит видео
    if not update.message.video:
        update.message.reply_text('Пожалуйста, отправьте видео для обрезки.')
        return

    # Получаем видео от пользователя
    video_file = update.message.video.get_file()
    video_file.download('video.mp4')

    # Создаем инлайн-кнопки для выбора секунд
    keyboard = [[InlineKeyboardButton("5 секунд", callback_data='5'),
                 InlineKeyboardButton("10 секунд", callback_data='10')],
                [InlineKeyboardButton("20 секунд", callback_data='20'),
                 InlineKeyboardButton("40 секунд", callback_data='40')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с выбором секунд
    update.message.reply_text('Выберите количество секунд для обрезки:', reply_markup=reply_markup)

    # Устанавливаем обработчик для выбора секунд
    query_handler = CallbackQueryHandler(cropvideo_chosen_duration, pattern=r'\d+')
    context.dispatcher.add_handler(query_handler)

def cropvideo_chosen_duration(update: Update, context: CallbackContext):
    query = update.callback_query
    duration = int(query.data)

    # Открываем видео с помощью moviepy
    video = VideoFileClip('video.mp4')
    video_duration = video.duration

    # Открываем видео с помощью moviepy
    video = VideoFileClip('video.mp4')

    # Обрезаем видео до указанной длительности
    cropped_video = video.subclip(0, duration)

    # Создаем инлайн-кнопки для выбора фильтра
    keyboard = [[InlineKeyboardButton("Без фильтра", callback_data='no_filter'),
                 InlineKeyboardButton("Черно-белый", callback_data='bw')],
                [InlineKeyboardButton("Негатив", callback_data='negative'),
                 InlineKeyboardButton("Сепия", callback_data='bw')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с выбором фильтра
    query.message.reply_text(f'Вы выбрали обрезать видео до {duration} секунд. Выберите фильтр для видео:', reply_markup=reply_markup)

    # Устанавливаем обработчик для выбора фильтра
    filter_handler = CallbackQueryHandler(apply_filter_to_video, pattern=r'no_filter|bw|negative|sepia')
    context.dispatcher.add_handler(filter_handler)

    # Сохраняем обрезанное видео во временный файл
    cropped_video.write_videofile('cropped_video.mp4')

    # Закрываем видеоклипы
    video.close()
    cropped_video.close()

def apply_filter_to_video(update: Update, context: CallbackContext):
    query = update.callback_query
    filter_name = query.data

    # Открываем обрезанное видео с помощью moviepy
    cropped_video = VideoFileClip('cropped_video.mp4')

    # Применяем выбранный фильтр
    if filter_name == 'bw':
        filtered_video = cropped_video.fx(vfx.blackwhite)
        filter_text = 'Черно-белый'
    elif filter_name == 'negative':
        filtered_video = cropped_video.fx(vfx.invert_colors)
        filter_text = 'Негатив'
    elif filter_name == 'sepia':
        filtered_video = cropped_video.fx(vfx.blackwhite)
        filter_text = 'Сепия'
    else:
        filtered_video = cropped_video
        filter_text = 'Без фильтра'

    # Отправляем сообщение о том, что видео обрабатывается
    query.message.reply_text(f'Ваше видео обрабатывается с фильтром "{filter_text}". Пожалуйста, ожидайте.')

    # Сохраняем видео с фильтром

    filtered_video.write_videofile('filtered_video.mp4')

    # Отправляем видео с фильтром пользователю
    with open('filtered_video.mp4', 'rb') as video_file:
        query.message.reply_video(video=video_file)

    # Удаляем временные файлы
    os.remove('video.mp4')
    os.remove('cropped_video.mp4')
    os.remove('filtered_video.mp4')

    # Закрываем видеоклипы
    cropped_video.close()
    filtered_video.close()


def handle_photos(update: Update, context: CallbackContext):
    if update.message.photo:
        file = update.message.photo[-1].get_file()
        file.download("photo.jpg")

        # Проверяем последнюю команду, отправленную пользователем
        last_command = context.user_data.get('last_command')

        if last_command == '/filter':
            aply_filter(update, context)
        elif last_command == '/cropimage':
            crop_image(update, context)
        elif last_command == '/adjust':
            adjust_image(update, context)
        else:
            # Если команда не была отправлена, просто игнорируем фото
            pass


def handle_videos(update: Update, context: CallbackContext):
    if update.message.video:
        file = update.message.video.get_file()
        file.download("video.mp4")
        cropvideo(update, context)

def main():
    updater = Updater(telegram_bot_token, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler("start", start)
    generate_handler = CommandHandler("generate", generate_text)
    filter_handler = CommandHandler("filter", aply_filter)
    crop_image_handler = CommandHandler("cropimage", crop_image)
    adjust_handler = CommandHandler('adjust', adjust_image)
    crop_video_handler = CommandHandler("cropvideo", cropvideo)
    photo_handler = MessageHandler(Filters.photo, handle_photos)
    video_handler = MessageHandler(Filters.video, handle_videos)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(generate_handler)
    dispatcher.add_handler(filter_handler)
    dispatcher.add_handler(crop_image_handler)
    dispatcher.add_handler(crop_video_handler)
    dispatcher.add_handler(photo_handler)
    dispatcher.add_handler(video_handler)
    #dispatcher.add_handler(CallbackQueryHandler(aply_chosen_filter))
    dispatcher.add_handler(adjust_handler)
    dispatcher.add_handler(CallbackQueryHandler(button_click))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
