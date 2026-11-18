from scr.instruments.risk_free_rate import RiskFreeRate

rf = RiskFreeRate()
rate = rf.compute(tmt_yrs=(600/365))

print(rate)

