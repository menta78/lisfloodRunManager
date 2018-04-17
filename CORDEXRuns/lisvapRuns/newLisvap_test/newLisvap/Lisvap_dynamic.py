# -------------------------------------------------------------------------
# Name:       Lisvap Model Dynamic
# Purpose:
#
# Author:      burekpe
#
# Created:     27/02/2014
# Copyright:   (c) burekpe 2014
# Licence:     <your licence>
# -------------------------------------------------------------------------


from global_modules.add1 import *

class LisvapModel_dyn(DynamicModel):

    # =========== DYNAMIC ====================================================

    def dynamic(self):
        """ Dynamic part of LISFLOOD
            calls the dynamic part of the hydrological modules
        """
        del timeMes[:]
        timemeasure("Start")

        self.CalendarDate = self.CalendarDayStart + \
            datetime.timedelta(days=self.currentTimeStep() * self.DtDay)
        self.CalendarDay = int(self.CalendarDate.strftime("%j"))
        # correct method to calculate the day of the year

        # Current calendar day (days [1...366], 1st of January = 1 , and so on)
      #  self.CalendarDay2 = self.currentTimeStep() * self.DtDay
        # Current calendar day (days [1...366], 1st of January = 1 , and so on)
      #  self.CalendarDay2 -= math.floor(self.CalendarDay2 / 365.25) * 365.25
        # self.CalendarDay=int(round(self.CalendarDay-math.floor(self.CalendarDay/365.25)*365.25))
        # correction such that daynumber 366 is regarded as day 1 again etc.
        # Takes into account leap years by setting year length to 365.25 days
        # Produces non-integer values but this is no problem here...

        i = self.currentTimeStep()
        self.TimeSinceStart = self.currentTimeStep() - self.firstTimeStep() + 1

        if Flags['loud']:
            print "%-6i %10s" %(self.currentTimeStep(),self.CalendarDate.strftime("%d/%m/%Y")) ,
        else:
            if not(Flags['check']):
                if (Flags['quiet']) and (not(Flags['veryquiet'])):
                    sys.stdout.write(".")
                if (not(Flags['quiet'])) and (not(Flags['veryquiet'])):
                    sys.stdout.write("\r%d" % i)
                    sys.stdout.flush()

        # ************************************************************
        """ up to here it was fun, now the real stuff starts
        """
        self.readmeteo_module.dynamic()
        timemeasure("Read meteo") # 1. timing after read input maps

        if Flags['check']: return  # if check than finish here

        """ Here it starts with meteorological modules:
        """

        ESatmin=0.6108*exp((17.27*self.TMin)/(self.TMin+237.3))
        ESatmax=0.6108*exp((17.27*self.TMax)/(self.TMax+237.3))
        ESat=(ESatmin+ESatmax)/2   # [KPa]

        # ************************************************************
        # ***** NET ABSORBED RADIATION *******************************
        # ************************************************************

        LatHeatVap = 2.501-0.002361*self.TAvg
        # latent heat of vaporization [MJ/kg]

        #EmNet = (0.34-0.14*sqrt(self.EAct))
        # Net emissivity
  #      RNUp = 4.903E-9 * (((self.TMin+273.16)**4)+((self.TMax+273.16)**4))/2
        # Up  longwave radiation [MJ/m2/day]


        RLN = self.Rdl - self.Rul
        RNA = pcraster.max(((1-self.AlbedoCanopy)*self.Rds + RLN)/LatHeatVap,scalar(0.0))
        RNAWater = pcraster.max(((1-self.AlbedoWater)*self.Rds + RLN)/LatHeatVap,scalar(0.0))


        # if we use net short and net long
  #      RSN = pcraster.max((self.Rds - self.Rus),scalar(0.0))   # net short
  #      RNA = pcraster.max((RSN + RLN)/LatHeatVap,scalar(0.0))
  #      RNAWater = RNA


        #RNA=pcraster.max(((1-self.AlbedoCanopy)*self.Rgd-RLN)/LatHeatVap,scalar(0.0))
        # net absorbed radiation of reference vegetation canopy [mm/d]
        #RNASoil=pcraster.max(((1-self.AlbedoSoil)*self.Rgd-RLN)/LatHeatVap,scalar(0.0))
        # net absorbed radiation of bare soil surface
        #RNAWater=pcraster.max(((1-self.AlbedoWater)*self.Rds + RLN)/LatHeatVap,scalar(0.0))
	    # net absorbed radiation of water surface


        VapPressDef = pcraster.max(ESat-self.EAct, scalar(0.0))
        Delta=((4098*ESat)/((self.TAvg+237.3)**2))
        # slope of saturated vapour pressure curve [mbar/deg C]
        Psycon = 0.665E-3*self.Psurf;
        #  psychrometric constant [kPa ?C-1]


        windpart= 900*self.Wind/(self.TAvg+273.16)
        denominator=Delta+Psycon*(1+0.34*self.Wind)
        numerator1=Delta/denominator
        numerator2=Psycon/denominator

        RNAN=RNA*numerator1
        #RNANSoil=RNASoil*numerator1
        RNANWater=RNAWater*numerator1

        EA=windpart*VapPressDef*numerator2


        # ************************************************************
        # ***** POTENTIAL REFERENCE EVAPO(TRANSPI)RATION ********
        # ************************************************************

        # Potential evapo(transpi)ration is calculated for three reference surfaces:

        # 1. Reference vegetation canopy
        # 2. Bare soil surface
        # 3. Open water surface

        self.ETRef=RNAN+EA
        # potential reference evapotranspiration rate [mm/day]
        #self.ESRef=RNANSoil+EA
        # potential evaporation rate from a bare soil surface [mm/day]
        self.EWRef=RNANWater+EA
        # potential evaporation rate from water surface [mm/day]

        self.sumET+=self.ETRef
        self.sumEW+=self.EWRef

        report(self.sumET/1826,'ETsum.map')
        report(self.sumEW/1826,'EWsum.map')

        # ************************************************************
        # ***** WRITING RESULTS: TIME SERIES AND MAPS ****************
        # ************************************************************

        self.output_module.dynamic()

        timemeasure("All")  # 10 timing after all
        for i in xrange(len(timeMes)):
            if self.currentTimeStep() == self.firstTimeStep():
                timeMesSum.append(timeMes[i] - timeMes[0])
            else:
                timeMesSum[i] += timeMes[i] - timeMes[0]

        # report(self.map2,'mapx.map')
        # self.Tss['UZTS'].sample(Precipitation)
        # self.report(self.Precipitation,binding['TaMaps'])
