import random
import os

# global variables
city_xyList = []
cityList = []
citySet = set()
edgeList = []
distDict = {}                   # {..., (cityNo1, cityNo2): dist , ...}
pDict = {}

# global functions
def readCityInfo(fileName):
# read coordinates info from file
    file = open(fileName, "r")
    for line in file.readlines():
        cityNo, cityX, cityY = line.split()
        
        cityList.append(int(cityNo))
        citySet.add(int(cityNo))
        city_xyList.append([int(cityNo), float(cityX), float(cityY)])
    #print(city_xyList)
    #print(cityList)
    
    # Calculate Euler distances
    for i in range (0, len(city_xyList)):
        for j in range (i + 1, len(city_xyList)):
            distXij = city_xyList[i][1] - city_xyList[j][1]
            distYij = city_xyList[i][2] - city_xyList[j][2]
            dist_ij = (distXij**2 + distYij**2)**0.5
            distDict[(city_xyList[i][0], city_xyList[j][0])] = float(dist_ij)
            edgeList.append((city_xyList[i][0], city_xyList[j][0]))
    #print(distDict)
    #print(edgeList)

class _ACO:
# Implement ACO algorithm
    def __init__(self, m = 30, Q = 80, alpha = 2,
                 rou = 0.3, beta = 5, ncMAX = 1000, c = 100):
    # Initialize m, alpha, beta, rou, ncMAX, Pheromone
        #if m <= len(cityList):
            #m = len(cityList) + 10
        self.m = m                        # ant number
        self.Q = Q                        # Constant Q
        self.alpha = alpha                # Constant ¦Á
        self.beta = beta                  # constant ¦Â
        self.rou = rou                    # Constant ¦Ñ
        self.ncMAX = ncMAX                # Execute Number
        self.bestAvg = 0
        self.bestLen = 0
        self.bestCity = []
        
        self.antList = []                 # ants
        for edge in edgeList:
            pDict[edge] = c
        #print(pDict)
        
    def putAnts(self):
    # put ants at random starting city
        for i in range(1, self.m + 1):
            startCity = random.choice(cityList)
            ant = _ant(startCity)
            self.antList.append(ant)
            #print(startCity)
        #print(len(antList))
        
    def updatePheromonoTrail(self):
    # update Pheromono Trail
        sumpDeltaDict = {}
        for edge in edgeList:
            pSum = 0.0
            for ant in self.antList:
                pSum += ant.pDeltaDict[edge]
            sumpDeltaDict[edge] = pSum
        for edge in edgeList:
            tempData = pDict[edge]
            pDict[edge] = (1 - self.rou) * tempData + sumpDeltaDict[edge]
                
    def search(self):
        bestLenFile = open("bestLen.txt", "w")
        cityFile = open("bestCity.txt", "w")
        avgFile = open("avgLen.txt", "w")
        avgList = []
        tempList1 = []
        tempList2 = []
        tempList3 = []
        for i in range(self.ncMAX + 1):
            # begin search
            self.antList = []
            self.putAnts()
            for ant in self.antList:
                while len(ant.allowedCitySet) != 0:
                    ant.MoveToNextCity(self.alpha, self.beta, self.Q)
                ant.updatepDelta(self.Q)
            # get result for current iter
            currBestLen = self.antList[0].currLen
            currBestTour = self.antList[0].tabuList
            for ant in self.antList:
                avgList.append(ant.currLen)
                if ant.currLen < currBestLen:
                    currBestLen = ant.currLen
                    currBestTour = ant.tabuList
            # print and record
            print(str(i)+":", currBestLen,":", currBestTour)
            avgCurr = sum(avgList)/len(avgList)
            tempList1.append(currBestLen)
            tempList2.append(currBestTour)
            tempList3.append(avgCurr)
            self.bestLen = min(tempList1)
            idx = tempList1.index(self.bestLen)
            self.bestCity = tempList2[idx]
            avgFile.write(str(avgCurr)+"\n")
            bestLenFile.write(str(currBestLen)+"\n")
            # update pheromono trail and reset ant
            self.updatePheromonoTrail()
            for ant in self.antList:
                city = random.choice(cityList)
                ant.setAnt(city)
        self.bestAvg = min(tempList3)
        print("Best Result:\n","Best Len:", self.bestLen,"\n Best City:", self.bestCity,"\n Avg Best:", self.bestAvg)
        cityFile.write(" ".join([str(x) for x in self.bestCity])+"\n"+str(self.bestLen))
        avgFile.write(str(self.bestAvg))
        avgFile.close()
        bestLenFile.close()
        cityFile.close()
        
class _ant:
# Implement Ant individual
    def __init__(self, currCity):
        self.setAnt(currCity)
        
    def setAnt(self, currCity):
        self.prevCity = None            # previous city
        self.currCity = currCity        # current city 
        self.currLen = 0                # Lk, current path length
        self.tabu = set()               # tabu city set
        self.tabuList = []              # tabu city set
        self.allowedCitySet = set()     # allowed city = citySet - tabu
        self.pDeltaDict = {}
        # init tabu and allowedCitySet
        self.tabu.add(int(currCity))
        self.tabuList.append(int(currCity))
        self.allowedCitySet = citySet - self.tabu
        # init pheromoneDeltaDict
        for edge in edgeList:
            self.pDeltaDict[edge] = 0        
    
    def updateAnt(self, city, Q):
    # update prevCity, currCity, pathLen, phenomoroDelta, tabu and allowed city table for ant
        if city > 0:
            # update prevCity and currCity
            self.prevCity = self.currCity
            self.currCity = city
            # update currLen, phernmono delta rijk
            if (self.prevCity > self.currCity):
                tempCitySet = (self.currCity, self.prevCity)
            else:
                tempCitySet = (self.prevCity, self.currCity)
            self.currLen += distDict[tempCitySet]
            # update tabuList and allowedCitySet
            self.tabu.add(int(city))
            self.tabuList.append(int(city))
            self.allowedCitySet = citySet - self.tabu
        return
    
    def updatepDelta(self, Q):
        # update phenomoroDelta
        i = 0
        j = 0
        while (i < len(self.tabuList)) and ((j + 1) < len(self.tabuList)):
            if self.tabuList[i] < self.tabuList[j + 1]:
                tempCitySet = (self.tabuList[i], self.tabuList[j + 1])
            else:
                tempCitySet = (self.tabuList[j + 1], self.tabuList[i])
            tempData = self.pDeltaDict[tempCitySet]
            self.pDeltaDict[tempCitySet] = tempData + Q / self.currLen
            i += 1
            j += 1
        return
    
    def MoveToNextCity(self, alpha, beta, Q):
    # Helper method to move an ant to next city
        nextCity = self.SelectNextCity(alpha, beta)
        self.updateAnt(nextCity, Q)
        
    def SelectNextCity(self, alpha, beta):
        if len(self.allowedCitySet) != 0:
            sumDividor = 0.0
            for probNextCity in self.allowedCitySet:
                if self.currCity > probNextCity:
                    tempCitySet = (probNextCity, self.currCity)
                else:
                    tempCitySet = (self.currCity, probNextCity)
                sumDividor += ((pDict[tempCitySet]) ** alpha) * ((1 / distDict[tempCitySet]) ** beta)
            probList = []
            for probNextCity in self.allowedCitySet:
                if self.currCity > probNextCity:
                    tempCitySet = (probNextCity, self.currCity)
                else:
                    tempCitySet = (self.currCity, probNextCity)
                if sumDividor != 0:
                    prob = (((pDict[tempCitySet]) ** alpha) * ((1 / distDict[tempCitySet]) ** beta)) / sumDividor
                else:
                    prob = 0.0
                probList.append((probNextCity, prob))
            # determine next city
            select = 0.0
            tempList = []
            idx = 0
            for (city, cityProb) in probList:
                if cityProb > select:
                    select = cityProb
            threshold = select * random.random()
    
            for (cityNum, cityProb) in probList:
                if cityProb >= threshold:
                    return cityNum
        return 0
        
if __name__ == "__main__":
    readCityInfo("30.txt")
    Aco = _ACO()
    Aco.search()