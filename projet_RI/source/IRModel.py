import operator
import numpy as np
import math
import EvalIRModel


class IRModel:

    def __init__(self, weighter):
        self.weighter = weighter

    def getScores(self, query):
        pass

    def getRanking(self, query):
        s = self.getScores(query)
        sort = sorted(s.items(), key=operator.itemgetter(1), reverse=True)
        return sort

    def getWeighter(self):
        return self.weighter

    def setParametre(self, *args):
        pass

    def findParametreOptimaux(self, *args):
        pass


class Vectoriel(IRModel):

    def __init__(self, weighter, normalized=False):
        super().__init__(weighter)
        self.normalized = normalized

    def getScores(self, query):

        query = self.weighter.getWeightsForQuery(query)

        score = dict()

        if self.normalized:
            pass

        else:
            for stem in query:
                weights_stem = self.weighter.getWeightsForStem(stem)
                for doc in weights_stem:
                    score[doc] = score.get(doc, 0) + weights_stem[doc] * query[stem]

        return score

    def __str__(self):
        return "Modèle Vectoriel" + (" normaliser" if self.normalized else " non normaliser") + '\nAvec ' + \
               str(self.weighter)


class Jelinek_Mercer(IRModel):

    def __init__(self, weighter, lambda_=0.2):
        super().__init__(weighter)
        self.lambda_ = lambda_

    def getScores(self, query):
        tailleCorpus = self.weighter.getLengthDocs()
        query = self.weighter.getWeightsForQuery(query)

        score = dict()

        for stem in query:
            tf_total = (1 - self.lambda_) * sum(nb for _, nb in self.weighter.getTfsForStem(stem).items()) / tailleCorpus

            weights_stem = self.weighter.getWeightsForStem(stem)

            for doc in weights_stem:
                # print("doc =",doc)
                # print("self.weighter.getLengthDoc(doc) =",self.weighter.getLengthDoc(doc))
                score[doc] = score.get(doc, 0) + (self.lambda_ * (weights_stem[doc] / self.weighter.getLengthDoc(doc))) + tf_total

        return score

    def setParametre(self, lambda_):
        self.lambda_ = lambda_

    def findParametreOptimaux(self, listeParametre, Queries, metrique="FMesure"):
        
        metriquePossible = {"Precision":0,  # La liste des metriques possible
                    "Rappel":1,
                    "FMesure":2,
                    "AvgP":3,
                    "reciprocalRank":4,
                    "Ndcg":5}
        
        metrique = metriquePossible[metrique]

        evaluation = EvalIRModel.EvalIRModel(Queries, self)
        
        scoreEvaluation = []
        for para in listeParametre:
            self.setParametre(para)
            scoreEvaluation.append(evaluation.evalModel())
            
        self.setParametre = listeParametre[scoreEvaluation.index(max(scoreEvaluation, key=lambda x: x[metrique][0]))]
        
    def __str__(self):
        return "Modèle Jelinek_Mercer, lambda = " + str(self.lambda_) + '\nAvec ' + str(self.weighter)


class Okapi(IRModel):

    def __init__(self, weighter, k1=0.75, b=1.2):
        super().__init__(weighter)
        self.k1 = k1
        self.b = b

    def getScores(self, query):

        query = self.weighter.getWeightsForQuery(query)

        score = dict()
        N = self.weighter.getNbDoc()

        moyenneMotDoc = self.weighter.getLengthDocs() / self.weighter.getNbDoc()

        for stem in query:

            docWithStem = self.weighter.getTfsForStem(stem)
            nStem = len(docWithStem)
            # idfStem = math.log((N - nStem + 0.5) / (nStem + 0.5))
            if nStem > 0:
                idfStem = math.log(N / nStem)

            for idDoc in docWithStem:
                freqStem = self.weighter.getTfsForStem(stem)[idDoc]

                bm25 = (freqStem * (self.k1 + 1)) / (freqStem + self.k1 * (1 - self.b + self.b * (self.weighter.getLengthDoc(idDoc) / moyenneMotDoc)))
                score[idDoc] = score.get(idDoc, 0) + idfStem * bm25

        return score

    def setParametre(self, *args):
        self.k1 = args[0]
        self.b = args[1]
        
    def findParametreOptimaux(self, listeParametre1, listeParametre2, Queries, metrique="FMesure"):
        
        metriquePossible = {"Precision":0,  # La liste des metriques possible
                    "Rappel":1,
                    "FMesure":2,
                    "AvgP":3,
                    "reciprocalRank":4,
                    "Ndcg":5}
        
        metrique = metriquePossible[metrique]
        
        evaluation = EvalIRModel.EvalIRModel(Queries, self)
        
        scoreEvaluation = []
        for para in listeParametre:
            self.setParametre(para)
            scoreEvaluation.append(evaluation.evalModel())
            
        self.setParametre = listeParametre[scoreEvaluation.index(max(scoreEvaluation, key=lambda x: x[metrique][0]))]
        
    
    def __str__(self):
        return "Modèle Okapi, ou BM25, k1 = " + str(self.k1) + ", b = " + str(self.b) +'\nAvec ' + str(self.weighter)