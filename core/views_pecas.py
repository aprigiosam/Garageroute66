from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, F
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from decimal import Decimal

from .models import (
    Peca, CategoriaPeca, Fornecedor, MovimentacaoEstoque
)
from .forms import (
    PecaForm, CategoriaPecaForm, FornecedorForm,
    MovimentacaoEstoqueForm, FiltroPecaForm
)


# ===== VIEWS DE PEÇAS =====

@login_required
def listar_pecas(request):
    """Lista todas as peças com filtros"""
    pecas = Peca.objects.select_related('categoria', 'fornecedor').order_by('nome')

    # Formulário de filtros
    filtro_form = FiltroPecaForm(request.GET)

    if filtro_form.is_valid():
        # Busca
        busca = filtro_form.cleaned_data.get('busca')
        if busca:
            pecas = pecas.filter(
                Q(codigo__icontains=busca) |
                Q(nome__icontains=busca) |
                Q(descricao__icontains=busca) |
                Q(codigo_fabricante__icontains=busca) |
                Q(codigo_barras__icontains=busca)
            )

        # Categoria
        categoria = filtro_form.cleaned_data.get('categoria')
        if categoria:
            pecas = pecas.filter(categoria=categoria)

        # Fornecedor
        fornecedor = filtro_form.cleaned_data.get('fornecedor')
        if fornecedor:
            pecas = pecas.filter(fornecedor=fornecedor)

        # Status do estoque
        estoque_status = filtro_form.cleaned_data.get('estoque')
        if estoque_status == 'baixo':
            pecas = pecas.filter(quantidade_estoque__lte=F('estoque_minimo'))
        elif estoque_status == 'critico':
            pecas = pecas.filter(quantidade_estoque__lte=F('estoque_minimo') * 0.5)
        elif estoque_status == 'ok':
            pecas = pecas.filter(quantidade_estoque__gt=F('estoque_minimo'))

        # Ativo/Inativo
        ativo = filtro_form.cleaned_data.get('ativo')
        if ativo:
            pecas = pecas.filter(ativo=(ativo == 'True'))

    # Paginação
    paginator = Paginator(pecas, 20)
    page_number = request.GET.get('page')
    pecas_page = paginator.get_page(page_number)

    # Estatísticas
    total_pecas = pecas.count()
    valor_total_estoque = pecas.aggregate(
        total=Sum(F('quantidade_estoque') * F('preco_custo'))
    )['total'] or Decimal('0.00')

    pecas_baixo = pecas.filter(quantidade_estoque__lte=F('estoque_minimo')).count()
    pecas_critico = pecas.filter(quantidade_estoque__lte=F('estoque_minimo') * 0.5).count()

    context = {
        'pecas': pecas_page,
        'filtro_form': filtro_form,
        'total_pecas': total_pecas,
        'valor_total_estoque': valor_total_estoque,
        'pecas_baixo': pecas_baixo,
        'pecas_critico': pecas_critico,
    }

    return render(request, 'core/pecas/listar_pecas.html', context)


@login_required
def cadastrar_peca(request):
    """Cadastrar nova peça"""
    if request.method == 'POST':
        form = PecaForm(request.POST, user=request.user)
        if form.is_valid():
            peca = form.save()
            messages.success(request, f'Peça {peca.codigo} - {peca.nome} cadastrada com sucesso!')
            return redirect('core:detalhes_peca', peca_id=peca.pk)
    else:
        form = PecaForm(user=request.user)

    context = {'form': form}
    return render(request, 'core/pecas/cadastrar_peca.html', context)


@login_required
def editar_peca(request, peca_id):
    """Editar peça existente"""
    peca = get_object_or_404(Peca, pk=peca_id)

    if request.method == 'POST':
        form = PecaForm(request.POST, instance=peca, user=request.user)
        if form.is_valid():
            peca = form.save()
            messages.success(request, f'Peça {peca.codigo} atualizada com sucesso!')
            return redirect('core:detalhes_peca', peca_id=peca.pk)
    else:
        form = PecaForm(instance=peca, user=request.user)

    context = {'form': form, 'peca': peca}
    return render(request, 'core/pecas/editar_peca.html', context)


@login_required
def detalhes_peca(request, peca_id):
    """Detalhes de uma peça com histórico de movimentações"""
    peca = get_object_or_404(
        Peca.objects.select_related('categoria', 'fornecedor'),
        pk=peca_id
    )

    # Movimentações (últimas 50)
    movimentacoes = peca.movimentacoes.select_related(
        'usuario', 'ordem_servico'
    ).order_by('-data_movimentacao')[:50]

    # Estatísticas da peça
    total_entradas = peca.movimentacoes.filter(
        tipo__in=[
            MovimentacaoEstoque.TipoMovimentacao.ENTRADA,
            MovimentacaoEstoque.TipoMovimentacao.DEVOLUCAO
        ]
    ).aggregate(total=Sum('quantidade'))['total'] or Decimal('0')

    total_saidas = peca.movimentacoes.filter(
        tipo__in=[
            MovimentacaoEstoque.TipoMovimentacao.SAIDA,
            MovimentacaoEstoque.TipoMovimentacao.PERDA
        ]
    ).aggregate(total=Sum('quantidade'))['total'] or Decimal('0')

    context = {
        'peca': peca,
        'movimentacoes': movimentacoes,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
    }

    return render(request, 'core/pecas/detalhes_peca.html', context)


# ===== VIEWS DE ESTOQUE =====

@login_required
def movimentacoes_estoque(request):
    """Lista todas as movimentações de estoque"""
    movimentacoes = MovimentacaoEstoque.objects.select_related(
        'peca', 'usuario', 'ordem_servico'
    ).order_by('-data_movimentacao')

    # Filtros
    tipo_filtro = request.GET.get('tipo')
    if tipo_filtro:
        movimentacoes = movimentacoes.filter(tipo=tipo_filtro)

    peca_filtro = request.GET.get('peca')
    if peca_filtro:
        movimentacoes = movimentacoes.filter(peca_id=peca_filtro)

    # Paginação
    paginator = Paginator(movimentacoes, 30)
    page_number = request.GET.get('page')
    movimentacoes_page = paginator.get_page(page_number)

    # Estatísticas
    total_movimentacoes = movimentacoes.count()
    valor_total = movimentacoes.aggregate(total=Sum('valor_total'))['total'] or Decimal('0.00')

    context = {
        'movimentacoes': movimentacoes_page,
        'total_movimentacoes': total_movimentacoes,
        'valor_total': valor_total,
        'tipos': MovimentacaoEstoque.TipoMovimentacao.choices,
    }

    return render(request, 'core/pecas/movimentacoes_estoque.html', context)


@login_required
def entrada_estoque(request):
    """Registrar entrada de estoque"""
    if request.method == 'POST':
        form = MovimentacaoEstoqueForm(request.POST, user=request.user)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.usuario = request.user

            # Forçar tipo como ENTRADA
            movimentacao.tipo = MovimentacaoEstoque.TipoMovimentacao.ENTRADA
            movimentacao.save()

            messages.success(
                request,
                f'Entrada registrada: {movimentacao.quantidade} {movimentacao.peca.get_unidade_medida_display()} '
                f'de {movimentacao.peca.nome}'
            )
            return redirect('core:detalhes_peca', peca_id=movimentacao.peca.pk)
    else:
        form = MovimentacaoEstoqueForm(user=request.user)
        # Pré-preencher tipo
        form.initial['tipo'] = MovimentacaoEstoque.TipoMovimentacao.ENTRADA

    context = {'form': form, 'titulo': 'Entrada de Estoque'}
    return render(request, 'core/pecas/movimentacao_form.html', context)


@login_required
def saida_estoque(request):
    """Registrar saída de estoque"""
    if request.method == 'POST':
        form = MovimentacaoEstoqueForm(request.POST, user=request.user)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.usuario = request.user

            # Forçar tipo como SAIDA
            movimentacao.tipo = MovimentacaoEstoque.TipoMovimentacao.SAIDA
            movimentacao.save()

            messages.success(
                request,
                f'Saída registrada: {movimentacao.quantidade} {movimentacao.peca.get_unidade_medida_display()} '
                f'de {movimentacao.peca.nome}'
            )
            return redirect('core:detalhes_peca', peca_id=movimentacao.peca.pk)
    else:
        form = MovimentacaoEstoqueForm(user=request.user)
        form.initial['tipo'] = MovimentacaoEstoque.TipoMovimentacao.SAIDA

    context = {'form': form, 'titulo': 'Saída de Estoque'}
    return render(request, 'core/pecas/movimentacao_form.html', context)


@login_required
def ajuste_estoque(request):
    """Ajustar estoque (inventário)"""
    if request.method == 'POST':
        form = MovimentacaoEstoqueForm(request.POST, user=request.user)
        if form.is_valid():
            movimentacao = form.save(commit=False)
            movimentacao.usuario = request.user
            movimentacao.tipo = MovimentacaoEstoque.TipoMovimentacao.AJUSTE
            movimentacao.save()

            messages.success(request, f'Estoque de {movimentacao.peca.nome} ajustado para {movimentacao.quantidade}')
            return redirect('core:detalhes_peca', peca_id=movimentacao.peca.pk)
    else:
        form = MovimentacaoEstoqueForm(user=request.user)
        form.initial['tipo'] = MovimentacaoEstoque.TipoMovimentacao.AJUSTE

    context = {'form': form, 'titulo': 'Ajuste de Estoque'}
    return render(request, 'core/pecas/movimentacao_form.html', context)


# ===== VIEWS DE CATEGORIAS E FORNECEDORES =====

@login_required
def listar_categorias(request):
    """Lista categorias de peças"""
    categorias = CategoriaPeca.objects.annotate(
        total_pecas=Count('pecas')
    ).order_by('nome')

    paginator = Paginator(categorias, 20)
    page_number = request.GET.get('page')
    categorias_page = paginator.get_page(page_number)

    context = {'categorias': categorias_page}
    return render(request, 'core/pecas/listar_categorias.html', context)


@login_required
def cadastrar_categoria(request):
    """Cadastrar categoria de peça"""
    if request.method == 'POST':
        form = CategoriaPecaForm(request.POST, user=request.user)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f'Categoria "{categoria.nome}" cadastrada com sucesso!')
            return redirect('core:listar_categorias')
    else:
        form = CategoriaPecaForm(user=request.user)

    context = {'form': form}
    return render(request, 'core/pecas/cadastrar_categoria.html', context)


@login_required
def listar_fornecedores(request):
    """Lista fornecedores"""
    fornecedores = Fornecedor.objects.annotate(
        total_pecas=Count('pecas')
    ).order_by('nome')

    busca = request.GET.get('busca')
    if busca:
        fornecedores = fornecedores.filter(
            Q(nome__icontains=busca) |
            Q(razao_social__icontains=busca) |
            Q(cnpj__icontains=busca)
        )

    paginator = Paginator(fornecedores, 20)
    page_number = request.GET.get('page')
    fornecedores_page = paginator.get_page(page_number)

    context = {'fornecedores': fornecedores_page}
    return render(request, 'core/pecas/listar_fornecedores.html', context)


@login_required
def cadastrar_fornecedor(request):
    """Cadastrar fornecedor"""
    if request.method == 'POST':
        form = FornecedorForm(request.POST, user=request.user)
        if form.is_valid():
            fornecedor = form.save()
            messages.success(request, f'Fornecedor "{fornecedor.nome}" cadastrado com sucesso!')
            return redirect('core:listar_fornecedores')
    else:
        form = FornecedorForm(user=request.user)

    context = {'form': form}
    return render(request, 'core/pecas/cadastrar_fornecedor.html', context)


# ===== API AJAX =====

@login_required
def api_buscar_peca(request):
    """Busca peças para autocomplete"""
    termo = request.GET.get('q', '')
    pecas = Peca.objects.filter(
        Q(codigo__icontains=termo) | Q(nome__icontains=termo),
        ativo=True
    ).select_related('categoria')[:10]

    resultados = [{
        'id': peca.id,
        'codigo': peca.codigo,
        'nome': peca.nome,
        'preco_venda': float(peca.preco_venda),
        'estoque': float(peca.quantidade_estoque),
        'unidade': peca.get_unidade_medida_display(),
    } for peca in pecas]

    return JsonResponse({'resultados': resultados})
