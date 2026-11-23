import numpy as np


class Maths:
    def __init__(
            self,
            actual: float | np.ndarray,
            predicted: float | np.ndarray,
    ) -> None:
        self.actual = actual
        self.predicted = predicted

    def compute_mae(self) -> float:
        mae = np.average(abs(self.actual - self.predicted))

        return mae

    def compute_mse(self) -> float:
        mse = np.average(abs(self.actual - self.predicted) ** 2)

        return mse

    def compute_rmse(
            self,
    ) -> float:
        mse = self.compute_mse()
        rmse = np.sqrt(mse)

        return rmse

    def compute_rmsle(
            self,
    ) -> float:
        rmsle = np.sqrt((np.average(np.log(self.actual + 1) - np.log(self.predicted + 1)) ** 2))

        return rmsle

    def compute_r2(
            self,
    ) -> float:
        numerator = (np.sum(np.pow((self.actual - self.predicted), 2)))
        denominator = (np.sum(np.pow((self.actual - np.mean(self.actual)), 2)))
        r2 = 1 - numerator / denominator
        return r2
