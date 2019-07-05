  

def getWarmingLevels(scenario, warmingLev):
  wly = {}
  if scenario == 'rcp85':
    if warmingLev == 1.5:
      wly = {
        'r1': 2024,
        'r2': 2033,
        'r3': 2025,
        'r4': 2028,
        'r5': 2029,
        'r6': 2025,
        'r7': 2027,
      }
    elif warmingLev == 2.:
      wly = {
        'r1': 2033,
        'r2': 2049,
        'r3': 2037,
        'r4': 2042,
        'r5': 2046,
        'r6': 2035,
        'r7': 2039,
      }
    elif warmingLev == 3.:
      wly = {
        'r1': 2053,
        'r2': 2077,
        'r3': 2055,
        'r4': 2066,
        'r5': 2074,
        'r6': 2052,
        'r7': 2061,
      }
    else:
      raise Exception('warming level not supported: ' + str(warmingLev)) 
  else:
    raise Exception('scenario not supported: ' + scenario)
  return wly



