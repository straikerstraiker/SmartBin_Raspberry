# SmartBin
Проект по поощрению раздельной сдачи мусора. Сдавай пластиковые бутылки и алюминиевые банки, получай баллы, обменивай их на бесплатные товары и скидки в магазинах-партнёрах. Проект представляет собой мобильное приложение, сервер с нейросетью Inception v3 и умную урну, ядром которой служит Raspberry Pi.

Компоненты, используемые в проекте:
1. Raspberry Pi 3 Model B
2. Raspberry Pi Camera V2.1
3. 4 сервопривода (MG996R, JX-PDI-6215MG)
4. 3 дальномера HC-SR04
5. Светодиодная RGB лента на чипе WS2801
6. Аналоговая светодиодная лента для внутреннего контейнера
7. I2C-контроллер сервоприводов PCA9685
8. Транзисторы MOSFET для контроля аналоговой ленты
9. Аудиосистема на 40 Вт
10. Цифровой бузер
11. Arduino Leonardo для контроля цифровой ленты
12. RFID-сканер RDM6300
13. Источник питания Robiton 6В с защитой от короткого замыкания
14. Источник питания 12В 8А для цифровой RGB ленты
15. Источник питания 12В 2А для аналоговой ленты
16. Источник питания 5В для Raspberry Pi и Arduino Leonardo
