## LgKumanda.py
LG televizyonunuzu internete bağladınızsa gizli menülere PC nizi kullanarak girebilirsiniz.
Bunun için python dilinde yazdığım programı (LgKumanda.py) kullanabilirsiniz:

1. PC nizle LG TV aynı networkde olmalı,
2. PC nizde Python 3.x kurulu olmalı.
3. programi kullanarak özellikle şu gizli menülere girebilirsiniz:

*   EZ_ADJUST menu için 255
*   IN START menu için 251
*   Installation menu için 207
*   POWER_ONLY mode için 254
*   UYARI: POWER_ONLY mode nedir bilmiyorsanız 254 GİRMEYİN!
*   Kayıt Başlatmak (Record) için 189

Installation menuden kurulum bilgilerinizi USB flash'a yedekleyip geri yükleyebilirsiniz.
Gizli menülerin bazısı şifre sorarsa 0413 ü deneyin. Şifreyi normal kumandayı kullanarak girebilirsiniz. 

"Factory reset" yapılmadıkça eşleme anahtarı değişmez, bu nedenle eşleme adımını atlamak LgKumanda.py dosyasını bir editor ile açın şu satırı size uygun hale getirin:

    lgtv["pairingKey"] = "DDGWAF"


# Faydalanilan Kaynaklar (This sowtware was developed with inspiration and/or information taken from):
----
This sowtware was developed with inspiration and/or information taken from:

*   <http://python.org>


*   <http://openlgtv.org.ru>


*   An application written in ruby: <https://github.com/dreamcat4/lgremote>