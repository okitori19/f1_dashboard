import pandas as pd
import os
import config

class CsvWriter:
    def __init__(self, logging):
        self.logging = logging


    def write(self, output_filename, df):
        output_path = config.DATA_DIR / output_filename
        df.to_csv(output_path, index=False)
        self.logging.info(f"Данные успешно сохранены в: {output_path}")
        return


    def write_with_append(self, output_filename, df):
        output_path = config.DATA_DIR / output_filename
        file_exists = os.path.isfile(output_path)  # Write header only if the file doesn't exist yet
        df.to_csv(output_path, mode="a", index=False, header=not file_exists)
        self.logging.info(f"Данные успешно сохранены в: {output_path}")
        return


    def write_with_check(self, output_filename, df, check_col):
        output_path = config.DATA_DIR / output_filename
        if os.path.exists(output_path):
            existing_numbers = pd.read_csv(output_path, usecols=[check_col])[check_col].astype(str).tolist()
            df_to_append = df[~df[check_col].astype(str).isin(existing_numbers)]
            
            # Если есть новые пилоты — дописываем их в конец файла (mode='a')
            if not df_to_append.empty:
                df_to_append.to_csv(output_path, mode='a', header=False, index=False)
                self.logging.info(f"Добавлено новых строк: {len(df_to_append)}")
            else:
                self.logging.info("Новых данных нет")
        else:
            # Если файла еще нет — создаем его с заголовками
            df.to_csv(output_path, mode='w', header=True, index=False)
            self.logging.info(f"Данные успешно сохранены в: {output_path}")
        return