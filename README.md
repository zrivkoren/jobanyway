# Программа для упрощения написания сопроводительных писем к вакансиям "JobAnyWay"

Программа автоматизирует процесс внесения персональной информации и деталей вакансии в сопроводительное письмо, генерирует "подсказки", позволяя создавать **уникальные** письма без необходимости каждый раз начинать с нуля.  
Требует ***индивидуальной доработки*** каждый раз, но при этом уходит гораздо меньше времени и усилий чем без нее.

## Основные функции и возможности
- **Формирование шаблона сопроводительного письма**  
 После написания n_го сопроводительного письма приходишь к некоему шаблону. Например: блок приветствия, блок с навыками, блок с заточенным под определенную вакансию/компанию содержимым, прощальный блок и так далее.  Можно создать свой шаблон с сопроводительным письмом, который не надо будет каждый раз писать

-  **Анализ ключевых навыков** Программа: 
	- анализирует описание вакансии на предмет ключевых навыков$\; 
	- сравнивает с хардскиллами кандидата;
	- формирует списки: 
		- совпадающие навыки; 
		- те, что есть в требованиях работодателя, но которых нет у кандидата;
		- хардскиллы кандидата, которые не требуются для данной работы, но возможно захочется ими похвастаться.		
- **Формирование шаблона текста для генерации ИИ**  
Можно составить шаблон запроса к ИИ для генерации уникального контента под определенную компанию и вакансию. 
- **Генерации текста искусственным интеллектом под определенную вакансию\компанию**  
	 Из страницы вакансии берется описание, дополняется информацией о компании (если она существует) и на основе пользовательского шаблона отправляется на генерацию разных вариантов AI. 
	 Используется библиотека g4f.	Полученный результат вставляется в шаблон всего сопроводительного письма. Сам текст промта выводится в консоль.	 
- **Сохранение результата**  
После генерации, содержимое сопроводительного письма сохраняется в текстовом файле в формате *дата-название_компании.txt* 
- **Открытие файла с результатом**  
По умолчанию файл с письмом открывается для дальнейших правок через Notepad++. Настройки выставляются в settings.py

## Установка проекта
1. Клонировать репозиторий и перейти в него

`https://github.com/zrivkoren/jobanyway.git`

2.  Создать и активировать виртуальное окружение

`python -m venv env`

`env/Scripts/activate`

3.  Обновить pip и установить зависимости

`python -m pip install --upgrade pip`

`pip install -r requirements.txt`

## Настройка (первые шаги)
- Переименуйте файлы: templates.py.sample, simple_vacancy.txt.sample, .env.sample, settings.py.sample **в** templates.py, simple_vacancy.txt, .env, settings.py  
  Это нужно сделать чтобы при обновлении у вас не стерлись ваши файлы настроек.
- Заполните файл .env своими данными, в том числе:
	- MAIN_VACATION_URL - адрес вакансии на habr или hh.ru, оставьте пустым если хотите сделать на основе  оффлайн вакансии,
	- RESUME_NAME - ваше имя,
	- MY_EMAIL - ваш email,
	- RESUME_SKILLS - свои хард скиллы (через запятую, без пробелов),
- При необходимости отредактируйте файл settings.py :
	- TEXT_EDITOR_PATH - путь до файла текстового редактора, через который будет редактироваться сопроводительное письмо. По умолчанию Notepad++
	- OPEN_LOCAL_COVER_LETTER - нужно ли открывать сгенерированное сопроводительное письмо в локальном текстовом редакторе. По умолчанию включено. Если **не** хотите открывать, то установите в False
- Напишите свой шаблон сопроводительного письма и текста для генерации ИИ в templates.py

## Как запускать
Вставьте ссылку на вакансию в файле .env в MAIN_VACATION_URL  
Запустите main.py

## Как пользоваться оффлайн вакансией
Если вакансия не на хабре или hh.ru, то можно скопировать ее в файл в simple_vacancy.txt. При это сохраняя следующую структуру:
Первая строка: url вакансии (можно оставить строку пустой)
2 строка: название компании
3: должность
4: зарплата (можно оставить строку пустой)
5 и далее строки: содержимое вакансии

Важно: в .env файле сделайте пустым MAIN_VACATION_URL= 

## Используемые технологии

- Python 3.11
- requests
- BeautifulSoup
- asyncio
- g4f

По вопросам можно обращаться в телеграм: https://t.me/zrivkoren1
