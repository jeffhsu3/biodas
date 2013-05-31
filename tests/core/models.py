from django.db import models

class BedEntry(models.Model):
    chrom = models.IntegerField(max_length = 2)
    start = models.IntegerField(max_length = 9)
    end = models.IntegerField(max_length = 9)
    gene = models.CharField(max_length = 300)
    strand = models.BooleanField()

    def __unicode__(self):
        return(self.gene)


class QTLEntry(models.Model):
    chrom = models.IntegerField(max_length = 2)
    start = models.IntegerField(max_length = 9)
    end = models.IntegerField(max_length = 9)
    gene = models.CharField(max_length = 300)
    strand = models.BooleanField()
    score = models.IntegerField(max_length = 3)

    def __unicode__(self):
        return(self.gene)

class SNPEntry(models.Model):
    chrom = models.IntegerField(max_length = 3)
    kent_bin =  models.IntegerField(max_length = 2000)
    start = models.IntegerField(max_length = 9)
    end = models.IntegerField(max_length = 9)
    counts = models.IntegerField(max_length = 10)
    rsID = models.CharField(max_length = 10)

    def __unicode__(self):
        return(self.gene)
