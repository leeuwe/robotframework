#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import inspect
import os.path

from robot.utils import is_list_like, Importer, normalize


class Languages:

    def __init__(self, languages=None):
        self.languages = []
        # The English singular forms are added for backwards compatibility
        self.headers = {
            'Setting': 'Settings',
            'Variable': 'Variables',
            'Test Case': 'Test Cases',
            'Task': 'Tasks',
            'Keyword': 'Keywords',
            'Comment': 'Comments'
        }
        self.settings = {}
        self.bdd_prefixes = set()
        self.true_strings = {'True', '1'}
        self.false_strings = {'False', '0', 'None', ''}
        for lang in self._get_languages(languages):
            self._add_language(lang)

    def reset(self, languages=None):
        self.__init__(languages)

    def add_language(self, name):
        self._add_language(Language.from_name(name))

    def _add_language(self, lang):
        if lang in self.languages:
            return
        self.languages.append(lang)
        self.headers.update({n.title(): lang.headers[n] for n in lang.headers if n})
        self.settings.update({n.title(): lang.settings[n] for n in lang.settings if n})
        self.bdd_prefixes |= {p.title() for p in lang.bdd_prefixes}
        self.true_strings |= {s.title() for s in lang.true_strings}
        self.false_strings |= {s.title() for s in lang.false_strings}

    def _get_languages(self, languages):
        languages = self._resolve_languages(languages)
        available = self._get_available_languages()
        returned = []
        for lang in languages:
            if isinstance(lang, Language):
                returned.append(lang)
            else:
                normalized = normalize(lang, ignore='-')
                if normalized in available:
                    returned.append(available[normalized]())
                else:
                    returned.extend(self._import_languages(lang))
        return returned

    def _resolve_languages(self, languages):
        if not languages:
            languages = []
        elif is_list_like(languages):
            languages = list(languages)
        else:
            languages = [languages]
        languages.append(En())
        return languages

    def _get_available_languages(self):
        available = {}
        for lang in Language.__subclasses__():
            available[normalize(lang.__name__)] = lang
            if lang.__doc__:
                available[normalize(lang.__doc__.splitlines()[0])] = lang
        return available

    def _import_languages(self, lang):
        def is_language(member):
            return (inspect.isclass(member)
                    and issubclass(member, Language)
                    and member is not Language)
        if os.path.exists(lang):
            lang = os.path.abspath(lang)
        module = Importer('language file').import_module(lang)
        return [value() for _, value in inspect.getmembers(module, is_language)]

    def __iter__(self):
        return iter(self.languages)


class Language:
    """Base class for language definitions.

    New translations can be added by extending this class and setting class
    attributes listed below.

    Language :attr:`code` is got based on the class name and :attr:`name`
    based on the docstring.
    """
    settings_header = None
    variables_header = None
    test_cases_header = None
    tasks_header = None
    keywords_header = None
    comments_header = None
    library_setting = None
    resource_setting = None
    variables_setting = None
    documentation_setting = None
    metadata_setting = None
    suite_setup_setting = None
    suite_teardown_setting = None
    test_setup_setting = None
    task_setup_setting = None
    test_teardown_setting = None
    task_teardown_setting = None
    test_template_setting = None
    task_template_setting = None
    test_timeout_setting = None
    task_timeout_setting = None
    test_tags_setting = None
    task_tags_setting = None
    keyword_tags_setting = None
    tags_setting = None
    setup_setting = None
    teardown_setting = None
    template_setting = None
    timeout_setting = None
    arguments_setting = None
    given_prefix = set()
    when_prefix = set()
    then_prefix = set()
    and_prefix = set()
    but_prefix = set()
    true_strings = set()
    false_strings = set()

    @classmethod
    def from_name(cls, name):
        """Return language class based on given `name`.

        Name can either be a language name (e.g. 'Finnish' or 'Brazilian Portuguese')
        or a language code (e.g. 'fi' or 'pt-BR'). Matching is case and space
        insensitive and the hyphen is ignored when matching language codes.

        Raises `ValueError` if no matching language is found.
        """
        normalized = normalize(name, ignore='-')
        for lang in cls.__subclasses__():
            if normalized == normalize(lang.__name__):
                return lang()
            if lang.__doc__ and normalized == normalize(lang.__doc__.splitlines()[0]):
                return lang()
        raise ValueError(f"No language with name '{name}' found.")

    @property
    def code(self):
        """Language code like 'fi' or 'pt-BR'.

        Got based on the class name. If the class name is two characters (or less),
        the code is just the name in lower case. If it is longer, a hyphen is added
        remainder of the class name is upper-cased.
        """
        code = type(self).__name__.lower()
        if len(code) < 3:
            return code
        return f'{code[:2]}-{code[2:].upper()}'

    @property
    def name(self):
        """Language name like 'Finnish' or 'Brazilian Portuguese'.

        Got from the first line of the class docstring.
        """
        return self.__doc__.splitlines()[0] if self.__doc__ else ''

    @property
    def headers(self):
        return {
            self.settings_header: En.settings_header,
            self.variables_header: En.variables_header,
            self.test_cases_header: En.test_cases_header,
            self.tasks_header: En.tasks_header,
            self.keywords_header: En.keywords_header,
            self.comments_header: En.comments_header
        }

    @property
    def settings(self):
        return {
            self.library_setting: En.library_setting,
            self.resource_setting: En.resource_setting,
            self.variables_setting: En.variables_setting,
            self.documentation_setting: En.documentation_setting,
            self.metadata_setting: En.metadata_setting,
            self.suite_setup_setting: En.suite_setup_setting,
            self.suite_teardown_setting: En.suite_teardown_setting,
            self.test_setup_setting: En.test_setup_setting,
            self.task_setup_setting: En.task_setup_setting,
            self.test_teardown_setting: En.test_teardown_setting,
            self.task_teardown_setting: En.task_teardown_setting,
            self.test_template_setting: En.test_template_setting,
            self.task_template_setting: En.task_template_setting,
            self.test_timeout_setting: En.test_timeout_setting,
            self.task_timeout_setting: En.task_timeout_setting,
            self.test_tags_setting: En.test_tags_setting,
            self.task_tags_setting: En.task_tags_setting,
            self.keyword_tags_setting: En.keyword_tags_setting,
            self.tags_setting: En.tags_setting,
            self.setup_setting: En.setup_setting,
            self.teardown_setting: En.teardown_setting,
            self.template_setting: En.template_setting,
            self.timeout_setting: En.timeout_setting,
            self.arguments_setting: En.arguments_setting,
        }

    @property
    def bdd_prefixes(self):
        return (self.given_prefix | self.when_prefix | self.then_prefix |
                self.and_prefix | self.but_prefix)

    def __eq__(self, other):
        return isinstance(other, type(self))

    def __hash__(self):
        return hash(type(self))


class En(Language):
    """English"""
    settings_header = 'Settings'
    variables_header = 'Variables'
    test_cases_header = 'Test Cases'
    tasks_header = 'Tasks'
    keywords_header = 'Keywords'
    comments_header = 'Comments'
    library_setting = 'Library'
    resource_setting = 'Resource'
    variables_setting = 'Variables'
    documentation_setting = 'Documentation'
    metadata_setting = 'Metadata'
    suite_setup_setting = 'Suite Setup'
    suite_teardown_setting = 'Suite Teardown'
    test_setup_setting = 'Test Setup'
    task_setup_setting = 'Task Setup'
    test_teardown_setting = 'Test Teardown'
    task_teardown_setting = 'Task Teardown'
    test_template_setting = 'Test Template'
    task_template_setting = 'Task Template'
    test_timeout_setting = 'Test Timeout'
    task_timeout_setting = 'Task Timeout'
    test_tags_setting = 'Test Tags'
    task_tags_setting = 'Task Tags'
    keyword_tags_setting = 'Keyword Tags'
    setup_setting = 'Setup'
    teardown_setting = 'Teardown'
    template_setting = 'Template'
    tags_setting = 'Tags'
    timeout_setting = 'Timeout'
    arguments_setting = 'Arguments'
    given_prefix = {'Given'}
    when_prefix = {'When'}
    then_prefix = {'Then'}
    and_prefix = {'And'}
    but_prefix = {'But'}
    true_strings = {'True', 'Yes', 'On'}
    false_strings = {'False', 'No', 'Off'}


class Cs(Language):
    """Czech"""
    settings_header = 'Nastavení'
    variables_header = 'Proměnné'
    test_cases_header = 'Testovací případy'
    tasks_header = 'Úlohy'
    keywords_header = 'Klíčová slova'
    comments_header = 'Komentáře'
    library_setting = 'Knihovna'
    resource_setting = 'Zdroj'
    variables_setting = 'Proměnná'
    documentation_setting = 'Dokumentace'
    metadata_setting = 'Metadata'
    suite_setup_setting = 'Příprava sady'
    suite_teardown_setting = 'Ukončení sady'
    test_setup_setting = 'Příprava testu'
    test_teardown_setting = 'Ukončení testu'
    test_template_setting = 'Šablona testu'
    test_timeout_setting = 'Časový limit testu'
    test_tags_setting = 'Štítky testů'
    task_setup_setting = 'Příprava úlohy'
    task_teardown_setting = 'Ukončení úlohy'
    task_template_setting = 'Šablona úlohy'
    task_timeout_setting = 'Časový limit úlohy'
    task_tags_setting = 'Štítky úloh'
    keyword_tags_setting = 'Štítky klíčových slov'
    tags_setting = 'Štítky'
    setup_setting = 'Příprava'
    teardown_setting = 'Ukončení'
    template_setting = 'Šablona'
    timeout_setting = 'Časový limit'
    arguments_setting = 'Argumenty'
    given_prefix = {'Pokud'}
    when_prefix = {'Když'}
    then_prefix = {'Pak'}
    and_prefix = {'A'}
    but_prefix = {'Ale'}
    true_strings = {'Pravda', 'Ano', 'Zapnuto'}
    false_strings = {'Nepravda', 'Ne', 'Vypnuto', 'Nic'}


class Nl(Language):
    """Dutch"""
    settings_header = 'Instellingen'
    variables_header = 'Variabelen'
    test_cases_header = 'Testgevallen'
    tasks_header = 'Taken'
    keywords_header = 'Sleutelwoorden'
    comments_header = 'Opmerkingen'
    library_setting = 'Bibliotheek'
    resource_setting = 'Resource'
    variables_setting = 'Variabele'
    documentation_setting = 'Documentatie'
    metadata_setting = 'Metadata'
    suite_setup_setting = 'Suite Preconditie'
    suite_teardown_setting = 'Suite Postconditie'
    test_setup_setting = 'Test Preconditie'
    test_teardown_setting = 'Test Postconditie'
    test_template_setting = 'Test Sjabloon'
    test_timeout_setting = 'Test Time-out'
    test_tags_setting = 'Test Labels'
    task_setup_setting = 'Taak Preconditie'
    task_teardown_setting = 'Taak Postconditie'
    task_template_setting = 'Taak Sjabloon'
    task_timeout_setting = 'Taak Time-out'
    task_tags_setting = 'Taak Labels'
    keyword_tags_setting = 'Sleutelwoord Labels'
    tags_setting = 'Labels'
    setup_setting = 'Preconditie'
    teardown_setting = 'Postconditie'
    template_setting = 'Sjabloon'
    timeout_setting = 'Time-out'
    arguments_setting = 'Parameters'
    given_prefix = {'Stel', 'Gegeven'}
    when_prefix = {'Als'}
    then_prefix = {'Dan'}
    and_prefix = {'En'}
    but_prefix = {'Maar'}
    true_strings = {'Waar', 'Ja', 'Aan'}
    false_strings = {'Onwaar', 'Nee', 'Uit', 'Geen'}


class Bs(Language):
    """Bosnian"""
    settings_header = 'Postavke'
    variables_header = 'Varijable'
    test_cases_header = 'Test Cases'
    tasks_header = 'Taskovi'
    keywords_header = 'Keywords'
    comments_header = 'Komentari'
    library_setting = 'Biblioteka'
    resource_setting = 'Resursi'
    variables_setting = 'Varijable'
    documentation_setting = 'Dokumentacija'
    metadata_setting = 'Metadata'
    suite_setup_setting = 'Suite Postavke'
    suite_teardown_setting = 'Suite Teardown'
    test_setup_setting = 'Test Postavke'
    test_teardown_setting = 'Test Teardown'
    test_template_setting = 'Test Template'
    test_timeout_setting = 'Test Timeout'
    test_tags_setting = 'Test Tagovi'
    task_setup_setting = 'Task Postavke'
    task_teardown_setting = 'Task Teardown'
    task_template_setting = 'Task Template'
    task_timeout_setting = 'Task Timeout'
    task_tags_setting = 'Task Tagovi'
    keyword_tags_setting = 'Keyword Tagovi'
    tags_setting = 'Tagovi'
    setup_setting = 'Postavke'
    teardown_setting = 'Teardown'
    template_setting = 'Template'
    timeout_setting = 'Timeout'
    arguments_setting = 'Argumenti'
    given_prefix = {'Uslovno'}
    when_prefix = {'Kada'}
    then_prefix = {'Tada'}
    and_prefix = {'I'}
    but_prefix = {'Ali'}


class Fi(Language):
    """Finnish"""
    settings_header = 'Asetukset'
    variables_header = 'Muuttujat'
    test_cases_header = 'Testit'
    tasks_header = 'Tehtävät'
    keywords_header = 'Avainsanat'
    comments_header = 'Kommentit'
    library_setting = 'Kirjasto'
    resource_setting = 'Resurssi'
    variables_setting = 'Muuttujat'
    documentation_setting = 'Dokumentaatio'
    metadata_setting = 'Metatiedot'
    suite_setup_setting = 'Setin Alustus'
    suite_teardown_setting = 'Setin Alasajo'
    test_setup_setting = 'Testin Alustus'
    task_setup_setting = 'Tehtävän Alustus'
    test_teardown_setting = 'Testin Alasajo'
    task_teardown_setting = 'Tehtävän Alasajo'
    test_template_setting = 'Testin Malli'
    task_template_setting = 'Tehtävän Malli'
    test_timeout_setting = 'Testin Aikaraja'
    task_timeout_setting = 'Tehtävän Aikaraja'
    test_tags_setting = 'Testin Tagit'
    task_tags_setting = 'Tehtävän Tagit'
    keyword_tags_setting = 'Avainsanan Tagit'
    tags_setting = 'Tagit'
    setup_setting = 'Alustus'
    teardown_setting = 'Alasajo'
    template_setting = 'Malli'
    timeout_setting = 'Aikaraja'
    arguments_setting = 'Argumentit'
    given_prefix = {'Oletetaan'}
    when_prefix = {'Kun'}
    then_prefix = {'Niin'}
    and_prefix = {'Ja'}
    but_prefix = {'Mutta'}
    true_strings = {'Tosi', 'Kyllä', 'Päällä'}
    false_strings = {'Epätosi', 'Ei', 'Pois'}


class Fr(Language):
    """French"""
    settings_header = 'Paramètres'
    variables_header = 'Variables'
    test_cases_header = 'Unités de test'
    tasks_header = 'Tâches'
    keywords_header = 'Mots-clés'
    comments_header = 'Commentaires'
    library_setting = 'Bibliothèque'
    resource_setting = 'Ressource'
    variables_setting = 'Variable'
    documentation_setting = 'Documentation'
    metadata_setting = 'Méta-donnée'
    suite_setup_setting = 'Mise en place de suite'
    suite_teardown_setting = 'Démontage de suite'
    test_setup_setting = 'Mise en place de test'
    test_teardown_setting = 'Démontage de test'
    test_template_setting = 'Modèle de test'
    test_timeout_setting = 'Délai de test'
    test_tags_setting = 'Étiquette de test'
    task_setup_setting = 'Mise en place de tâche'
    task_teardown_setting = 'Démontage de test'
    task_template_setting = 'Modèle de tâche'
    task_timeout_setting = 'Délai de tâche'
    task_tags_setting = 'Étiquette de tâche'
    keyword_tags_setting = 'Etiquette de mot-clé'
    tags_setting = 'Étiquette'
    setup_setting = 'Mise en place'
    teardown_setting = 'Démontage'
    template_setting = 'Modèle'
    timeout_setting = "Délai d'attente"
    arguments_setting = 'Arguments'
    given_prefix = {'Étant donné'}
    when_prefix = {'Lorsque'}
    then_prefix = {'Alors'}
    and_prefix = {'Et'}
    but_prefix = {'Mais'}
    true_strings = {'Vrai', 'Oui', 'Actif'}
    false_strings = {'Faux', 'Non', 'Désactivé', 'Aucun'}


class De(Language):
    """German"""
    settings_header = 'Einstellungen'
    variables_header = 'Variablen'
    test_cases_header = 'Testfälle'
    tasks_header = 'Aufgaben'
    keywords_header = 'Schlüsselwörter'
    comments_header = 'Kommentare'
    library_setting = 'Bibliothek'
    resource_setting = 'Ressource'
    variables_setting = 'Variablen'
    documentation_setting = 'Dokumentation'
    metadata_setting = 'Metadaten'
    suite_setup_setting = 'Suitevorbereitung'
    suite_teardown_setting = 'Suitenachbereitung'
    test_setup_setting = 'Testvorbereitung'
    test_teardown_setting = 'Testnachbereitung'
    test_template_setting = 'Testvorlage'
    test_timeout_setting = 'Testzeitlimit'
    test_tags_setting = 'Test Marker'
    task_setup_setting = 'Aufgabenvorbereitung'
    task_teardown_setting = 'Aufgabennachbereitung'
    task_template_setting = 'Aufgabenvorlage'
    task_timeout_setting = 'Aufgabenzeitlimit'
    task_tags_setting = 'Aufgaben Marker'
    keyword_tags_setting = 'Schlüsselwort Marker'
    tags_setting = 'Marker'
    setup_setting = 'Vorbereitung'
    teardown_setting = 'Nachbereitung'
    template_setting = 'Vorlage'
    timeout_setting = 'Zeitlimit'
    arguments_setting = 'Argumente'
    given_prefix = {'Angenommen'}
    when_prefix = {'Wenn'}
    then_prefix = {'Dann'}
    and_prefix = {'Und'}
    but_prefix = {'Aber'}
    true_strings = {'Wahr', 'Ja', 'An', 'Ein'}
    false_strings = {'Falsch', 'Nein', 'Aus', 'Unwahr'}


class PtBr(Language):
    """Brazilian Portuguese"""
    settings_header = 'Configurações'
    variables_header = 'Variáveis'
    test_cases_header = 'Casos de Teste'
    tasks_header = 'Tarefas'
    keywords_header = 'Palavras-Chave'
    comments_header = 'Comentários'
    library_setting = 'Biblioteca'
    resource_setting = 'Recurso'
    variables_setting = 'Variável'
    documentation_setting = 'Documentação'
    metadata_setting = 'Metadados'
    suite_setup_setting = 'Configuração da Suíte'
    suite_teardown_setting = 'Finalização de Suíte'
    test_setup_setting = 'Inicialização de Teste'
    test_teardown_setting = 'Finalização de Teste'
    test_template_setting = 'Modelo de Teste'
    test_timeout_setting = 'Tempo Limite de Teste'
    test_tags_setting = 'Test Tags'
    task_setup_setting = 'Inicialização de Tarefa'
    task_teardown_setting = 'Finalização de Tarefa'
    task_template_setting = 'Modelo de Tarefa'
    task_timeout_setting = 'Tempo Limite de Tarefa'
    task_tags_setting = 'Task Tags'
    keyword_tags_setting = 'Keyword Tags'
    tags_setting = 'Etiquetas'
    setup_setting = 'Inicialização'
    teardown_setting = 'Finalização'
    template_setting = 'Modelo'
    timeout_setting = 'Tempo Limite'
    arguments_setting = 'Argumentos'
    given_prefix = {'Dado'}
    when_prefix = {'Quando'}
    then_prefix = {'Então'}
    and_prefix = {'E'}
    but_prefix = {'Mas'}
    true_strings = {'Verdadeiro', 'Verdade', 'Sim', 'Ligado'}
    false_strings = {'Falso', 'Não', 'Desligado', 'Desativado', 'Nada'}


class Pt(Language):
    """Portuguese"""
    settings_header = 'Definições'
    variables_header = 'Variáveis'
    test_cases_header = 'Casos de Teste'
    tasks_header = 'Tarefas'
    keywords_header = 'Palavras-Chave'
    comments_header = 'Comentários'
    library_setting = 'Biblioteca'
    resource_setting = 'Recurso'
    variables_setting = 'Variável'
    documentation_setting = 'Documentação'
    metadata_setting = 'Metadados'
    suite_setup_setting = 'Inicialização de Suíte'
    suite_teardown_setting = 'Finalização de Suíte'
    test_setup_setting = 'Inicialização de Teste'
    test_teardown_setting = 'Finalização de Teste'
    test_template_setting = 'Modelo de Teste'
    test_timeout_setting = 'Tempo Limite de Teste'
    test_tags_setting = 'Etiquetas de Testes'
    task_setup_setting = 'Inicialização de Tarefa'
    task_teardown_setting = 'Finalização de Tarefa'
    task_template_setting = 'Modelo de Tarefa'
    task_timeout_setting = 'Tempo Limite de Tarefa'
    task_tags_setting = 'Etiquetas de Tarefas'
    keyword_tags_setting = 'Etiquetas de Palavras-Chave'
    tags_setting = 'Etiquetas'
    setup_setting = 'Inicialização'
    teardown_setting = 'Finalização'
    template_setting = 'Modelo'
    timeout_setting = 'Tempo Limite'
    arguments_setting = 'Argumentos'
    given_prefix = {'Dado'}
    when_prefix = {'Quando'}
    then_prefix = {'Então'}
    and_prefix = {'E'}
    but_prefix = {'Mas'}
    true_strings = {'Verdadeiro', 'Verdade', 'Sim', 'Ligado'}
    false_strings = {'Falso', 'Não', 'Desligado', 'Desativado', 'Nada'}


class Th(Language):
    """Thai"""
    settings_header = 'การตั้งค่า'
    variables_header = 'กำหนดตัวแปร'
    test_cases_header = 'การทดสอบ'
    tasks_header = 'งาน'
    keywords_header = 'คำสั่งเพิ่มเติม'
    comments_header = 'คำอธิบาย'
    library_setting = 'ชุดคำสั่งที่ใช้'
    resource_setting = 'ไฟล์ที่ใช้'
    variables_setting = 'ชุดตัวแปร'
    documentation_setting = 'เอกสาร'
    metadata_setting = 'รายละเอียดเพิ่มเติม'
    suite_setup_setting = 'กำหนดค่าเริ่มต้นของชุดการทดสอบ'
    suite_teardown_setting = 'คืนค่าของชุดการทดสอบ'
    test_setup_setting = 'กำหนดค่าเริ่มต้นของการทดสอบ'
    task_setup_setting = 'กำหนดค่าเริ่มต้นของงาน'
    test_teardown_setting = 'คืนค่าของการทดสอบ'
    task_teardown_setting = 'คืนค่าของงาน'
    test_template_setting = 'โครงสร้างของการทดสอบ'
    task_template_setting = 'โครงสร้างของงาน'
    test_timeout_setting = 'เวลารอของการทดสอบ'
    task_timeout_setting = 'เวลารอของงาน'
    test_tags_setting = 'กลุ่มของการทดสอบ'
    task_tags_setting = 'กลุ่มของงาน'
    keyword_tags_setting = 'กลุ่มของคำสั่งเพิ่มเติม'
    setup_setting = 'กำหนดค่าเริ่มต้น'
    teardown_setting = 'คืนค่า'
    template_setting = 'โครงสร้าง'
    tags_setting = 'กลุ่ม'
    timeout_setting = 'หมดเวลา'
    arguments_setting = 'ค่าที่ส่งเข้ามา'
    given_prefix = {'กำหนดให้'}
    when_prefix = {'เมื่อ'}
    then_prefix = {'ดังนั้น'}
    and_prefix = {'และ'}
    but_prefix = {'แต่'}


class Pl(Language):
    """Polish"""
    settings_header = 'Ustawienia'
    variables_header = 'Zmienne'
    test_cases_header = 'Przypadki testowe'
    tasks_header = 'Zadania'
    keywords_header = 'Słowa kluczowe'
    comments_header = 'Komentarze'
    library_setting = 'Biblioteka'
    resource_setting = 'Zasób'
    variables_setting = 'Zmienne'
    documentation_setting = 'Dokumentacja'
    metadata_setting = 'Metadane'
    suite_setup_setting = 'Inicjalizacja zestawu'
    suite_teardown_setting = 'Ukończenie zestawu'
    test_setup_setting = 'Inicjalizacja testu'
    test_teardown_setting = 'Ukończenie testu'
    test_template_setting = 'Szablon testu'
    test_timeout_setting = 'Limit czasowy testu'
    test_tags_setting = 'Znaczniki testu'
    task_setup_setting = 'Inicjalizacja zadania'
    task_teardown_setting = 'Ukończenie zadania'
    task_template_setting = 'Szablon zadania'
    task_timeout_setting = 'Limit czasowy zadania'
    task_tags_setting = 'Znaczniki zadania'
    keyword_tags_setting = 'Znaczniki słowa kluczowego'
    tags_setting = 'Znaczniki'
    setup_setting = 'Inicjalizacja'
    teardown_setting = 'Ukończenie'
    template_setting = 'Szablon'
    timeout_setting = 'Limit czasowy'
    arguments_setting = 'Argumenty'
    given_prefix = {'Zakładając', 'Zakładając, że', 'Mając'}
    when_prefix = {'Jeżeli', 'Jeśli', 'Gdy', 'Kiedy'}
    then_prefix = {'Wtedy'}
    and_prefix = {'Oraz', 'I'}
    but_prefix = {'Ale'}


class Uk(Language):
    """Ukrainian"""
    settings_header = 'Налаштування'
    variables_header = 'Змінні'
    test_cases_header = 'Тест-кейси'
    tasks_header = 'Завдань'
    keywords_header = 'Ключових слова'
    comments_header = 'Коментарів'
    library_setting = 'Бібліотека'
    resource_setting = 'Ресурс'
    variables_setting = 'Змінна'
    documentation_setting = 'Документація'
    metadata_setting = 'Метадані'
    suite_setup_setting = 'Налаштування Suite'
    suite_teardown_setting = 'Розбірка Suite'
    test_setup_setting = 'Налаштування тесту'
    test_teardown_setting = 'Розбирання тестy'
    test_template_setting = 'Тестовий шаблон'
    test_timeout_setting = 'Час тестування'
    test_tags_setting = 'Тестові теги'
    task_setup_setting = 'Налаштування завдання'
    task_teardown_setting = 'Розбір завдання'
    task_template_setting = 'Шаблон завдання'
    task_timeout_setting = 'Час очікування завдання'
    task_tags_setting = 'Теги завдань'
    keyword_tags_setting = 'Теги ключових слів'
    tags_setting = 'Теги'
    setup_setting = 'Встановлення'
    teardown_setting = 'Cпростовувати пункт за пунктом'
    template_setting = 'Шаблон'
    timeout_setting = 'Час вийшов'
    arguments_setting = 'Аргументи'
    given_prefix = {'Дано'}
    when_prefix = {'Коли'}
    then_prefix = {'Тоді'}
    and_prefix = {'Та'}
    but_prefix = {'Але'}


class Es(Language):
    """Spanish"""
    settings_header = 'Configuraciones'
    variables_header = 'Variables'
    test_cases_header = 'Casos de prueba'
    tasks_header = 'Tareas'
    keywords_header = 'Palabras clave'
    comments_header = 'Comentarios'
    library_setting = 'Biblioteca'
    resource_setting = 'Recursos'
    variables_setting = 'Variable'
    documentation_setting = 'Documentación'
    metadata_setting = 'Metadatos'
    suite_setup_setting = 'Configuración de la Suite'
    suite_teardown_setting = 'Desmontaje de la Suite'
    test_setup_setting = 'Configuración de prueba'
    test_teardown_setting = 'Desmontaje de la prueba'
    test_template_setting = 'Plantilla de prueba'
    test_timeout_setting = 'Tiempo de espera de la prueba'
    test_tags_setting = 'Etiquetas de la prueba'
    task_setup_setting = 'Configuración de tarea'
    task_teardown_setting = 'Desmontaje de tareas'
    task_template_setting = 'Plantilla de tareas'
    task_timeout_setting = 'Tiempo de espera de las tareas'
    task_tags_setting = 'Etiquetas de las tareas'
    keyword_tags_setting = 'Etiquetas de palabras clave'
    tags_setting = 'Etiquetas'
    setup_setting = 'Configuración'
    teardown_setting = 'Desmontaje'
    template_setting = 'Plantilla'
    timeout_setting = 'Tiempo agotado'
    arguments_setting = 'Argumentos'
    given_prefix = {'Dado'}
    when_prefix = {'Cuando'}
    then_prefix = {'Entonces'}
    and_prefix = {'Y'}
    but_prefix = {'Pero'}
    true_strings = {'Verdadero', 'Si', 'On'}
    false_strings = {'Falso', 'No', 'Off', 'Ninguno'}


class Ru(Language):
    """Russian"""
    settings_header = 'Настройки'
    variables_header = 'Переменные'
    test_cases_header = 'Заголовки тестов'
    tasks_header = 'Задача'
    keywords_header = 'Ключевые слова'
    comments_header = 'Комментарии'
    library_setting = 'Библиотека'
    resource_setting = 'Ресурс'
    variables_setting = 'Переменные'
    documentation_setting = 'Документация'
    metadata_setting = 'Метаданные'
    suite_setup_setting = 'Инициализация комплекта тестов'
    suite_teardown_setting = 'Завершение комплекта тестов'
    test_setup_setting = 'Инициализация теста'
    test_teardown_setting = 'Завершение теста'
    test_template_setting = 'Шаблон теста'
    test_timeout_setting = 'Лимит выполнения теста'
    test_tags_setting = 'Теги тестов'
    task_setup_setting = 'Инициализация задания'
    task_teardown_setting = 'Завершение задания'
    task_template_setting = 'Шаблон задания'
    task_timeout_setting = 'Лимит задания'
    task_tags_setting = 'Метки заданий'
    keyword_tags_setting = 'Метки ключевых слов'
    tags_setting = 'Метки'
    setup_setting = 'Инициализация'
    teardown_setting = 'Завершение'
    template_setting = 'Шаблон'
    timeout_setting = 'Лимит'
    arguments_setting = 'Аргументы'
    given_prefix = {'Дано'}
    when_prefix = {'Когда'}
    then_prefix = {'Тогда'}
    and_prefix = {'И'}
    but_prefix = {'Но'}


class ZhCn(Language):
    """Chinese Simplified"""
    settings_header = '设置'
    variables_header = '变量'
    test_cases_header = '用例'
    tasks_header = '任务'
    keywords_header = '关键字'
    comments_header = '备注'
    library_setting = '程序库'
    resource_setting = '资源文件'
    variables_setting = '变量文件'
    documentation_setting = '说明'
    metadata_setting = '元数据'
    suite_setup_setting = '用例集启程'
    suite_teardown_setting = '用例集终程'
    test_setup_setting = '用例启程'
    test_teardown_setting = '用例终程'
    test_template_setting = '用例模板'
    test_timeout_setting = '用例超时'
    test_tags_setting = '用例标签'
    task_setup_setting = '任务启程'
    task_teardown_setting = '任务终程'
    task_template_setting = '任务模板'
    task_timeout_setting = '任务超时'
    task_tags_setting = '任务标签'
    keyword_tags_setting = '关键字标签'
    tags_setting = '标签'
    setup_setting = '启程'
    teardown_setting = '终程'
    template_setting = '模板'
    timeout_setting = '超时'
    arguments_setting = '参数'
    given_prefix = {'假定'}
    when_prefix = {'当'}
    then_prefix = {'那么'}
    and_prefix = {'并且'}
    but_prefix = {'但是'}
    true_strings = {'真', '是', '开'}
    false_strings = {'假', '否', '关', '空'}


class ZhTw(Language):
    """Chinese Traditional"""
    settings_header = '設置'
    variables_header = '變量'
    test_cases_header = '案例'
    tasks_header = '任務'
    keywords_header = '關鍵字'
    comments_header = '備註'
    library_setting = '函式庫'
    resource_setting = '資源文件'
    variables_setting = '變量文件'
    documentation_setting = '說明'
    metadata_setting = '元數據'
    suite_setup_setting = '測試套啟程'
    suite_teardown_setting = '測試套終程'
    test_setup_setting = '測試啟程'
    test_teardown_setting = '測試終程'
    test_template_setting = '測試模板'
    test_timeout_setting = '測試逾時'
    test_tags_setting = '測試標籤'
    task_setup_setting = '任務啟程'
    task_teardown_setting = '任務終程'
    task_template_setting = '任務模板'
    task_timeout_setting = '任務逾時'
    task_tags_setting = '任務標籤'
    keyword_tags_setting = '關鍵字標籤'
    tags_setting = '標籤'
    setup_setting = '啟程'
    teardown_setting = '終程'
    template_setting = '模板'
    timeout_setting = '逾時'
    arguments_setting = '参数'
    given_prefix = {'假定'}
    when_prefix = {'當'}
    then_prefix = {'那麼'}
    and_prefix = {'並且'}
    but_prefix = {'但是'}
    true_strings = {'真', '是', '開'}
    false_strings = {'假', '否', '關', '空'}


class Tr(Language):
    """Turkish"""
    settings_header = 'Ayarlar'
    variables_header = 'Değişkenler'
    test_cases_header = 'Test Durumları'
    tasks_header = 'Görevler'
    keywords_header = 'Anahtar Kelimeler'
    comments_header = 'Yorumlar'
    library_setting = 'Kütüphane'
    resource_setting = 'Kaynak'
    variables_setting = 'Değişkenler'
    documentation_setting = 'Dokümantasyon'
    metadata_setting = 'Üstveri'
    suite_setup_setting = 'Takım Kurulumu'
    suite_teardown_setting =  'Takım Bitişi'
    test_setup_setting = 'Test Kurulumu'
    task_setup_setting = 'Görev Kurulumu'
    test_teardown_setting = 'Test Bitişi'
    task_teardown_setting = 'Görev Bitişi'
    test_template_setting = 'Test Taslağı'
    task_template_setting = 'Görev Taslağı'
    test_timeout_setting = 'Test Zaman Aşımı'
    task_timeout_setting = 'Görev Zaman Aşımı'
    test_tags_setting = 'Test Etiketleri'
    task_tags_setting = 'Görev Etiketleri'
    keyword_tags_setting = 'Anahtar Kelime Etiketleri'
    setup_setting = 'Kurulum'
    teardown_setting = 'Bitiş'
    template_setting = 'Taslak'
    tags_setting = 'Etiketler'
    timeout_setting = 'Zaman Aşımı'
    arguments_setting = 'Argümanlar'
    given_prefix = {'Diyelim ki'}
    when_prefix = {'Eğer ki'}
    then_prefix = {'O zaman'}
    and_prefix = {'Ve'}
    but_prefix = {'Ancak'}
    true_strings = {'Doğru', 'Evet', 'Açik'}
    false_strings = {'Yanliş', 'Hayir', 'Kapali'}


class Sv(Language):
    """Swedish"""
    settings_header = 'Inställningar'
    variables_header = 'Variabler'
    test_cases_header = 'Testfall'
    tasks_header = 'Taskar'
    keywords_header = 'Nyckelord'
    comments_header = 'Kommentarer'
    library_setting = 'Bibliotek'
    resource_setting = 'Resurs'
    variables_setting = 'Variabel'
    documentation_setting = 'Dokumentation'
    metadata_setting = 'Metadata'
    suite_setup_setting = 'Svit konfigurering'
    suite_teardown_setting = 'Svit nedrivning'
    test_setup_setting = 'Test konfigurering'
    test_teardown_setting = 'Test nedrivning'
    test_template_setting = 'Test mall'
    test_timeout_setting = 'Test timeout'
    test_tags_setting = 'Test taggar'
    task_setup_setting = 'Task konfigurering'
    task_teardown_setting = 'Task nedrivning'
    task_template_setting = 'Task mall'
    task_timeout_setting = 'Task timeout'
    task_tags_setting = 'Arbetsuppgift taggar'
    keyword_tags_setting = 'Nyckelord taggar'
    tags_setting = 'Taggar'
    setup_setting = 'Konfigurering'
    teardown_setting = 'Nedrivning'
    template_setting = 'Mall'
    timeout_setting = 'Timeout'
    arguments_setting = 'Argument'
    given_prefix = {'Givet'}
    when_prefix = {'När'}
    then_prefix = {'Då'}
    and_prefix = {'Och'}
    but_prefix = {'Men'}
    true_strings = {'Sant', 'Ja', 'På'}
    false_strings = {'Falskt', 'Nej', 'Av', 'Ingen'}


class Bg(Language):
    """Bulgarian"""
    settings_header = 'Настройки'
    variables_header = 'Променливи'
    test_cases_header = 'Тестови случаи'
    tasks_header = 'Задачи'
    keywords_header = 'Ключови думи'
    comments_header = 'Коментари'
    library_setting = 'Библиотека'
    resource_setting = 'Ресурс'
    variables_setting = 'Променлива'
    documentation_setting = 'Документация'
    metadata_setting = 'Метаданни'
    suite_setup_setting = 'Първоначални настройки на комплекта'
    suite_teardown_setting = 'Приключване на комплекта'
    test_setup_setting = 'Първоначални настройки на тестове'
    test_teardown_setting = 'Приключване на тестове'
    test_template_setting = 'Шаблон за тестове'
    test_timeout_setting = 'Таймаут за тестове'
    test_tags_setting = 'Етикети за тестове'
    task_setup_setting = 'Първоначални настройки на задачи'
    task_teardown_setting = 'Приключване на задачи'
    task_template_setting = 'Шаблон за задачи'
    task_timeout_setting = 'Таймаут за задачи'
    task_tags_setting = 'Етикети за задачи'
    keyword_tags_setting = 'Етикети за ключови думи'
    tags_setting = 'Етикети'
    setup_setting = 'Първоначални настройки'
    teardown_setting = 'Приключване'
    template_setting = 'Шаблон'
    timeout_setting = 'Таймаут'
    arguments_setting = 'Аргументи'
    given_prefix = {'В случай че'}
    when_prefix = {'Когато'}
    then_prefix = {'Тогава'}
    and_prefix = {'И'}
    but_prefix = {'Но'}
    true_strings = {'Вярно', 'Да', 'Включен'}
    false_strings = {'Невярно', 'Не', 'Изключен', 'Нищо'}


class Ro(Language):
    """Romanian"""
    settings_header = 'Setari'
    variables_header = 'Variabile'
    test_cases_header = 'Cazuri De Test'
    tasks_header = 'Sarcini'
    keywords_header = 'Cuvinte Cheie'
    comments_header = 'Comentarii'
    library_setting = 'Librarie'
    resource_setting = 'Resursa'
    variables_setting = 'Variabila'
    documentation_setting = 'Documentatie'
    metadata_setting = 'Metadate'
    suite_setup_setting = 'Configurare De Suita'
    suite_teardown_setting = 'Configurare De Intrerupere'
    test_setup_setting = 'Setare De Test'
    test_teardown_setting = 'Inrerupere De Test'
    test_template_setting = 'Sablon De Test'
    test_timeout_setting = 'Timp Expirare Test'
    test_tags_setting = 'Taguri De Test'
    task_setup_setting = 'Configuarare activitate'
    task_teardown_setting = 'Intrerupere activitate'
    task_template_setting = 'Sablon de activitate'
    task_timeout_setting = 'Timp de expirare activitate'
    task_tags_setting = 'Etichete activitate'
    keyword_tags_setting = 'Etichete metode'
    tags_setting = 'Etichete'
    setup_setting = 'Setare'
    teardown_setting = 'Intrerupere'
    template_setting = 'Sablon'
    timeout_setting = 'Expirare'
    arguments_setting = 'Argumente'
    given_prefix = {'Fie ca'}
    when_prefix = {'Cand'}
    then_prefix = {'Atunci'}
    and_prefix = {'Si'}
    but_prefix = {'Dar'}
    true_strings = {'Adevarat', 'Da', 'Cand'}
    false_strings = {'Fals', 'Nu', 'Oprit', 'Niciun'}


class It(Language):
    """Italian"""
    settings_header = 'Impostazioni'
    variables_header = 'Variabili'
    test_cases_header = 'Casi Di Test'
    tasks_header = 'Attività'
    keywords_header = 'Parole Chiave'
    comments_header = 'Commenti'
    library_setting = 'Libreria'
    resource_setting = 'Risorsa'
    variables_setting = 'Variabile'
    documentation_setting = 'Documentazione'
    metadata_setting = 'Metadati'
    suite_setup_setting = 'Configurazione Suite'
    suite_teardown_setting = 'Distruzione Suite'
    test_setup_setting = 'Configurazione Test'
    test_teardown_setting = 'Distruzione Test'
    test_template_setting = 'Modello Test'
    test_timeout_setting = 'Timeout Test'
    test_tags_setting = 'Tag Del Test'
    task_setup_setting = 'Configurazione Attività'
    task_teardown_setting = 'Distruzione Attività'
    task_template_setting = 'Modello Attività'
    task_timeout_setting = 'Timeout Attività'
    task_tags_setting = 'Tag Attività'
    keyword_tags_setting = 'Tag Parola Chiave'
    tags_setting = 'Tag'
    setup_setting = 'Configurazione'
    teardown_setting = 'Distruzione'
    template_setting = 'Template'
    timeout_setting = 'Timeout'
    arguments_setting = 'Parametri'
    given_prefix = {'Dato'}
    when_prefix = {'Quando'}
    then_prefix = {'Allora'}
    and_prefix = {'E'}
    but_prefix = {'Ma'}
    true_strings = {'Vero', 'Sì', 'On'}
    false_strings = {'Falso', 'No', 'Off', 'Nessuno'}
from robot.conf import Language


class Hi(Language):
    """Hindi"""
    settings_header = 'स्थापना'
    variables_header = 'चर'
    test_cases_header = 'जांच पड़ताल'
    tasks_header = 'कार्य नियत कार्य'
    keywords_header = 'कुंजीशब्द'
    comments_header = 'टिप्पणी'
    library_setting = 'कोड़ प्रतिबिंब संग्रह'
    resource_setting = 'संसाधन'
    variables_setting = 'चर'
    documentation_setting = 'प्रलेखन'
    metadata_setting = 'अधि-आंकड़ा'
    suite_setup_setting = 'जांच की शुरुवात'
    suite_teardown_setting = 'परीक्षण कार्य अंत'
    test_setup_setting = 'परीक्षण कार्य प्रारंभ'
    test_teardown_setting = 'परीक्षण कार्य अंत'
    test_template_setting = 'परीक्षण ढांचा'
    test_timeout_setting = 'परीक्षण कार्य समय समाप्त'
    test_tags_setting = 'जाँचका उपनाम परीक्षणका उपनाम'
    task_setup_setting = 'परीक्षण कार्य प्रारंभ'
    task_teardown_setting = 'परीक्षण कार्य अंत'
    task_template_setting = 'परीक्षण ढांचा'
    task_timeout_setting = 'कार्य समयबाह्य'
    task_tags_setting = 'जाँचका उपनाम परीक्षणका उपनाम'
    keyword_tags_setting = 'मुख्य शब्द का उपनाम कुंजीशब्द का उपनाम'
    tags_setting = 'निशान'
    setup_setting = 'व्यवस्थापन रूपरचना ढांचा'
    teardown_setting = 'विमोचन'
    template_setting = 'साँचा'
    timeout_setting = 'समय समाप्त'
    arguments_setting = 'प्राचल'
    given_prefix = {'दिया हुआ'}
    when_prefix = {'जब'}
    then_prefix = {'तब'}
    and_prefix = {'और'}
    but_prefix = {'परंतु'}
    true_strings = {'यथार्थ', 'निश्चित', 'हां', 'पर'}
    false_strings = {'गलत', 'नहीं', 'हालाँकि', 'यद्यपि', 'नहीं', 'हैं'}
