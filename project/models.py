from django.db import models

class Content (models.Model):
    name = models.TextField("Наименование")
    type = models.ForeignKey("Type", on_delete=models.CASCADE,null=True)
  
  
    class Meta:
        verbose_name="Контент"
        verbose_name_plural="Контент"
        

class Type (models.Model):
    name= models.TextField("Наименование")

    class Meta:
        verbose_name="Вид"
        verbose_name_plural="Виды"

    def __str__(self):
        return self.name
        