from flask import Flask, render_template, request, redirect, url_for
from app import app
from models.models import db, User

@app.route('/', methods=['GET', 'POST'])
def home():
        if request.method == 'POST':
                name = request.form.get('name')
        
                # Create a new user and add it to the database
                new_user = User(name=name)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('home'))
        
        users = User.query.all()
        return render_template('home/index.html', users=users)

@app.route('/edit/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('home/partials/user_update.html', user=user)


@app.route('/update/<int:user_id>', methods=['GET', 'PUT'])
def update_user(user_id):
        
        print(request.form)  # This will print the incoming form data
        
        user = User.query.get(user_id)
        if not user:
                return "User not found", 404

        
        
        if request.method == 'PUT':    
                name = request.form.get('name')
                
                if not name:
                    return "Missing name parameter", 400
            
                user.name = name
                db.session.commit()
                
                
                # Return the updated row as HTML to replace the old row
                return render_template('home/partials/user_tr.html', user=user)

        return render_template('home/partials/user_tr.html', user=user)

@app.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    db.session.delete(user)
    db.session.commit()

    # Return an empty response with 204 status (No Content) to signal to HTMX to remove the row
    return render_template('home/partials/user_list.html', user=user)