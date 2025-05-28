from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.main.forms import VaultForm, AccountForm, CategoryForm, SearchForm, CustomFieldForm
from app.models import User, Account, Vault, Category, Tag, AccountHistory, AccessLog
from app.utils.crypto import encrypt_password, decrypt_password
from datetime import datetime
import json

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    vaults = current_user.vaults.all()
    recent_accounts = Account.query.filter_by(user_id=current_user.id).order_by(Account.last_accessed.desc()).limit(5).all()
    favorite_accounts = Account.query.filter_by(user_id=current_user.id, is_favorite=True).all()
    return render_template('index.html', vaults=vaults, recent_accounts=recent_accounts, favorite_accounts=favorite_accounts)

# Vault routes
@bp.route('/vaults')
@login_required
def vaults():
    vaults = current_user.vaults.all()
    return render_template('vaults/index.html', vaults=vaults)

@bp.route('/vaults/new', methods=['GET', 'POST'])
@login_required
def new_vault():
    form = VaultForm()
    if form.validate_on_submit():
        vault = Vault(
            name=form.name.data,
            description=form.description.data,
            icon=form.icon.data,
            user_id=current_user.id
        )
        db.session.add(vault)
        db.session.commit()
        flash('Vault created successfully!', 'success')
        return redirect(url_for('main.vaults'))
    return render_template('vaults/new.html', form=form)

@bp.route('/vaults/<int:id>')
@login_required
def view_vault(id):
    vault = Vault.query.get_or_404(id)
    if vault.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.vaults'))
    accounts = vault.accounts.all()
    return render_template('vaults/view.html', vault=vault, accounts=accounts)

# Account routes
@bp.route('/accounts/new', methods=['GET', 'POST'])
@login_required
def new_account():
    form = AccountForm()
    form.vault_id.choices = [(v.id, v.name) for v in current_user.vaults.all()]
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    
    if form.validate_on_submit():
        encrypted_password = encrypt_password(form.password.data)
        tags = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
        
        account = Account(
            title=form.title.data,
            username=form.username.data,
            encrypted_password=encrypted_password,
            url=form.url.data,
            notes=form.notes.data,
            icon=form.icon.data,
            is_favorite=form.is_favorite.data,
            password_expires_at=form.password_expires_at.data,
            vault_id=form.vault_id.data,
            category_id=form.category_id.data,
            user_id=current_user.id
        )
        
        # Handle tags
        for tag_name in tags:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            account.tags.append(tag)
        
        db.session.add(account)
        db.session.commit()
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.view_vault', id=form.vault_id.data))
    
    return render_template('accounts/new.html', form=form)

@bp.route('/accounts/<int:id>')
@login_required
def view_account(id):
    account = Account.query.get_or_404(id)
    if account.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    # Log access
    log = AccessLog(
        account_id=account.id,
        user_id=current_user.id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        action='view'
    )
    account.last_accessed = datetime.utcnow()
    db.session.add(log)
    db.session.commit()
    
    return render_template('accounts/view.html', account=account)

@bp.route('/accounts/<int:id>/password')
@login_required
def get_password(id):
    account = Account.query.get_or_404(id)
    if account.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Log password access
    log = AccessLog(
        account_id=account.id,
        user_id=current_user.id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        action='password_view'
    )
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'password': decrypt_password(account.encrypted_password)})

@bp.route('/accounts/<int:id>/toggle-favorite', methods=['POST'])
@login_required
def toggle_favorite(id):
    account = Account.query.get_or_404(id)
    if account.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    account.is_favorite = not account.is_favorite
    db.session.commit()
    
    return jsonify({'is_favorite': account.is_favorite})

# Search routes
@bp.route('/search')
@login_required
def search():
    form = SearchForm()
    form.vault.choices = [(v.id, v.name) for v in current_user.vaults.all()]
    form.category.choices = [(c.id, c.name) for c in Category.query.all()]
    
    query = request.args.get('query', '')
    vault_id = request.args.get('vault', type=int)
    category_id = request.args.get('category', type=int)
    favorites_only = request.args.get('favorites_only', type=bool)
    
    accounts = Account.query.filter_by(user_id=current_user.id)
    
    if query:
        accounts = accounts.filter(
            (Account.title.ilike(f'%{query}%')) |
            (Account.username.ilike(f'%{query}%')) |
            (Account.url.ilike(f'%{query}%')) |
            (Account.notes.ilike(f'%{query}%'))
        )
    
    if vault_id:
        accounts = accounts.filter_by(vault_id=vault_id)
    
    if category_id:
        accounts = accounts.filter_by(category_id=category_id)
    
    if favorites_only:
        accounts = accounts.filter_by(is_favorite=True)
    
    accounts = accounts.all()
    return render_template('search.html', form=form, accounts=accounts)

# Category routes
@bp.route('/categories')
@login_required
def categories():
    categories = Category.query.all()
    return render_template('categories/index.html', categories=categories)

@bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            icon=form.icon.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('main.categories'))
    return render_template('categories/new.html', form=form)

# Custom fields routes
@bp.route('/accounts/<int:id>/custom-fields/new', methods=['POST'])
@login_required
def add_custom_field(id):
    account = Account.query.get_or_404(id)
    if account.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    form = CustomFieldForm()
    if form.validate_on_submit():
        custom_fields = account.custom_fields or {}
        custom_fields[form.field_name.data] = form.field_value.data
        account.custom_fields = custom_fields
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid form data'}), 400 