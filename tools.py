import pandas as pd


def performance(prices):
    """
    Простое получение доходности через np.cumprod(), последовательное перемножение
    """
    if not len(prices):
        return prices    
    returns = (prices / prices.shift(1)).fillna(1)
    return returns.cumprod() - 1


def drawdown(prices, is_max=False):
    """
    Максимальная просадка доходности
    """
    if not len(prices):
        return prices
    
    total = len(prices.index)
    rolling_max = prices.rolling(total, min_periods=1).max()
    drawdown = prices / rolling_max - 1.0
    if is_max:
        return drawdown.rolling(total, min_periods=1).min()
    return drawdown


def rate_for_period(rate, T=1):
    """
    Процент за период
    rate - исходная доходность
    T - кол-во периодов исходной доходности
    """
    P = 1 + rate
    p = (P ** (1 / T) - 1)
    return (p + 1) - 1


def sharpe_ratio(er, rf, stdev):
    """
    Коэф. Шарпа
    er - средняя доходность за период
    rf - безрисковая ставка за период
    stdev - стандартное отклонение доходности
    """
    return (er - rf) / stdev


class Schedule(object):
    """
    Расписание по рабочим дням в желаемый период. 
    
    :param start: начальная дата
    :param end: конечная дата 
    :param dates: даты торговой истории
    """
    def __init__(self, start, end, dates=None):
        # создаем расписание из рабочих дней
        df = pd.DataFrame([], index=pd.date_range(start, end, freq='B'))
        
        # filter dates in schedule, which not exist
        if dates is not None:
            df = df[df.index.isin(dates)].copy()
        
        # заполняем полезные данные
        df['date'] = df.index
        df['weekday'] = df['date'].dt.weekday
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['week'] = df['date'].dt.week
        df['allow'] = False
        df['done'] = False
        
        self.schedule = df
        
    def mark_rebalance_days(self, day, freq):
        """
        Помечаем дни, когда разрешена ребалансировка

        :param day: порядковый номер дня, аналогичен индексам массивов
        :param freq: период ребалансировки
        """
        if freq not in ['year', 'month', 'week', 'day']:
            raise ValueError(f'Wrong frequency {fred}')

        df = self.schedule
        df['allow'] = False
        df.iloc[0, df.columns.get_loc('allow')] = True  # allow rebalance at the start
            
        if freq == 'day':
            df['allow'] = True
            return df
        elif freq == 'week':
            groupby = ['year', 'week']
        elif freq == 'month':
            groupby = ['year', 'month']
        elif freq == 'year':
            groupby = ['year']

        # группировка и пометка дней ребалансировки
        grouped = df.groupby(groupby)
        for idx, grp in grouped:
            if len(grp) >= abs(day):
                df.loc[grp.iloc[day].name, 'allow'] = True

        return df