import pandas as pd

class DataPreProcessor:
    def __init__(self, data, isNested, nestedColumn, metaColumn):
        if isNested:
            self.__dataframe_ = pd.json_normalize(data, 
                                                  record_path = [nestedColumn], 
                                                  meta = metaColumn,
                                                  record_prefix = nestedColumn + "_")
        else:
            self.__dataframe_ = pd.DataFrame(data)
    
    def pp_selectData(self, columnList):
        data = self.__dataframe_[columnList].copy()
        return data
    
    def pp_selectDataIndexed(self, columnList, indexColumn):
        data = self.__dataframe_[columnList].copy()
        data.set_index(indexColumn, inplace=True)
        return data
    
    def pp_selectDataTransformed(self, columnList, indexColumn):
        data = self.__dataframe_[columnList].copy()
        data.set_index(indexColumn, inplace=True)
        return data