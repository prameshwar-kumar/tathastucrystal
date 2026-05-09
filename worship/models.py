# worship/models.py
from django.conf import settings
from django.db.models import Avg
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator

class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField("Category Name", max_length=200, unique=True)
    image = models.ImageField("Category Image", upload_to="categories/", blank=True, null=True)
    show_in_homepage = models.BooleanField("Show in Homepage", default=False)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200]
            slug = base
            counter = 1
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('worship:category_detail', kwargs={'slug': self.slug})


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    short_description = models.CharField(max_length=400, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    weight = models.DecimalField("Weight (g)", max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    length = models.DecimalField("Length (cm)", max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    width = models.DecimalField("Width (cm)", max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    height = models.DecimalField("Height (cm)", max_digits=6, decimal_places=2, validators=[MinValueValidator(0)], blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def dimensions(self):
        if self.length and self.width and self.height:
            return f"{self.length} × {self.width} × {self.height} cm"
        return "N/A"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:220]
            slug = base
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('worship:product_detail', kwargs={'slug': self.slug})

    def effective_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def main_image_url(self):
        first = self.images.first()
        if first:
            return first.image.url
        return None

    @property
    def discount_percentage(self):
        if self.discount_price and self.price and self.price > 0:
            discount = (self.price - self.discount_price) / self.price * 100
            return round(discount)
        return 0

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(a=Avg('rating'))['a']
        return round(avg) if avg else 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first")

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"

    def __str__(self):
        return f"Image {self.pk} for {self.product.name}"


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='worship_reviews'
    )
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class ProductQA(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='qas'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='worship_qas'
    )
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
