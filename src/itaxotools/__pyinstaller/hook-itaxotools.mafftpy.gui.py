# Include all package data

from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('itaxotools.common.resources')
datas += collect_data_files('itaxotools.mafftpy')
datas += collect_data_files('itaxotools.mafftpy.gui')
