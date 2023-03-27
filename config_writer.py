import types


class ConfigController:
    def __init__(self, config):
        self.config = config
        self.config_file = "config.ini"

    def __str__(self):
        """Control config. writes and deletes stuff"""

    def _delete_all_info(self, headline):
        for sub_headlines in self.config[headline]:
            self.config.remove_option(headline, sub_headlines)

    def _setter(self, headline, constant, value):
        if not isinstance(value, types.FunctionType):
            self.config.set(headline, constant, str(value))

    def _simple_settings_writer(self, setting_dict):
        for headline in setting_dict:
            for sub_headline in setting_dict[headline]:
                self._setter(headline, sub_headline, setting_dict[headline][sub_headline])

    def _writer(self):
        with open(self.config_file, "w") as config_file:
            self.config.write(config_file)

    def controller(self, setting_dict, delete_all=False):
        if delete_all:
            for headline in setting_dict:
                self._delete_all_info(headline)

            self._simple_settings_writer(setting_dict)

        self._writer()