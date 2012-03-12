Internationalization
====================

*Internationalization* (often abbreviated *i18n* since there are 18
characters between the first "i" and the last "n" in that word) allows
Evennia's core server to return texts in other languages than English -
without anyone having to go in and add it manually. Take a look at the
``locale`` directory of the Evennia installation, there you will find
which languages are currently supported.

Note, what is translated in this way are hard-coded strings from the
server, things like "Connection closed" or "Server restarted".
Basically, the things users are not supposed to change on their own.
This means that the default command set is *not* translated. The reason
for this is that commands are *intended* to be modified by users.

Changing server language
------------------------

Change language by copy&pasting the following from the default file to
your ``game/settings.py`` file:

::

    USE_I18N = True
    LANGUAGE_CODE = 'en'

Here ``'en'`` should be changed to the abbreviation for one of the
supported languages found in ``locale/``. Restart the server to activate
i18n.

Translating Evennia
-------------------

If you cannot find your language in ``locale/`` it's because noone has
translated it yet. Alternatively you might have the language but find
the translation bad ... You are welcome to help improve the situation!

To start a new translation, place yourself in Evennia's root directory
and run

::

    django-admin makemessages -l <language-code>

where ``<language-code>`` is the two-letter locale code for the language
you want, like 'sv' for Swedish or 'es' for Spanish.

Next head to ``locale/<language-code>/LC_MESSAGES`` and edit the
``*.po`` file you find there. There is no need to edit this file using a
normal text editor -- best is to use a po-file editor from the web
(search the web for "po editor" for many free alternatives).

The concept of translating is simple, it's just a matter of taking the
english strings you find in the ``*.po`` file and add your language's
translation best you can.

Finally, you need to compile your translation into a more efficient
form.

::

    django-admin compilemessages

This will go through all languages and create/update compiled files
(``*.mo``) for them. This needs to be done whenever a ``*.po`` file is
updated.

When you are done, send the ``*.po`` and ``*.mo`` file to the Evennia
developer list (or push it into your own repository clone) so we can
integrate your translation into Evennia!