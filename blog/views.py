from blog.models import Article
from django.views.generic import ListView, DetailView, UpdateView, \
    DeleteView, CreateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    fields = ('title', 'body', 'preview',)
    success_url = reverse_lazy('blog:list')


class ArticleListView(LoginRequiredMixin, ListView):
    model = Article

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_published=True)
        return queryset


class ArticleDetailView(LoginRequiredMixin, DetailView):
    model = Article
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset=queryset)
        self.object.views_count += 1
        self.object.save()
        return self.object


class ArticleUpdateView(LoginRequiredMixin, UpdateView):
    model = Article
    fields = ('title', 'body', 'preview',)

    def get_success_url(self):
        return reverse('blog:view', args=[self.kwargs.get('pk')])


class ArticleDeleteView(LoginRequiredMixin, DeleteView):
    model = Article
    success_url = reverse_lazy('blog:list')
