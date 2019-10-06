from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.exceptions import NotFound

import os

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/Playlister')

app = Flask(__name__)  # Flask app
client = MongoClient(host=f'{host}?retryWrites=false')  # Mongo client

db = client.get_default_database()  # New db with name of Playlister
playlists = db.playlists  # create playlists comment
comments = db.comments


@app.route('/')
def playlists_index():
    """Show all playlists."""
    return render_template('playlists_index.html', playlists=playlists.find())  # Return an iterable of all playlists in db


@app.route('/playlists', methods=['POST'])
def paylists_submit():
    """Submit a new playlist."""
    #playlist = request.form.to_dict()
    playlist = { 
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'rating': request.form.get('rating'),
        'videos': request.form.get('videos').split(),
        'created_at': datetime.datetime.today()
    }
    playlist_id = playlists.insert_one(playlist).inserted_id
    return redirect(url_for('playlists_show', playlist_id=playlist_id))


@app.route('/playlists/new')
def playlists_new():
    """Create a new playlist"""
    return render_template('playlists_new.html', playlist={}, title='New Playlist')


@app.route('/playlists/<playlist_id>')
def playlists_show(playlist_id):
    """Show a single playlist."""
    playlist_id = ObjectId(playlist_id)
    playlist = playlists.find_one({'_id': playlist_id})
    playlist_comments = comments.find({'playlist_id': playlist_id})
    return render_template('playlists_show.html', playlist=playlist, comments=playlist_comments)


@app.route('/playlists/<playlist_id>', methods=['POST'])
def playlists_update(playlist_id):
    """Submit an edited playlist."""
    updated_playlist = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'rating': request.form.get('rating'),
        'videos': request.form.get('videos').split(),
        'created_at': datetime.datetime.today()
    }
    playlists.update_one({'_id': ObjectId(playlist_id)},
                         {'$set': updated_playlist})
    return redirect(url_for('playlists_show', playlist_id=playlist_id))


@app.route('/playlists/<playlist_id>/edit')
def playlists_edit(playlist_id):
    # TODO: Have rating value auto select instead of reseting back to 1 in edit form.
    """Show the edit form for a playlist."""
    playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
    video_links = '\n'.join(playlist.get('videos'))  # Huh?
    return render_template('playlists_edit.html', playlist=playlist, title='Edit Playlist')


@app.route('/playlists/<playlist_id>/delete', methods=['POST'])
def playlists_delete(playlist_id):
    """Delete one playlist."""
    playlists.delete_one({'_id': ObjectId(playlist_id)})
    return redirect(url_for('playlists_index'))


@app.route('/playlists/comments', methods=['POST'])
def comments_new():
    """Submit a new comment."""
    playlist_id = ObjectId(request.form.get('playlist_id'))
    comment = {
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'playlist_id': playlist_id
    }
    comment_id = comments.insert_one(comment).inserted_id
    return redirect(url_for('playlists_show', playlist_id=playlist_id))

@app.route('/playlists/comments/<comment_id>', methods=['POST'])
def comments_delete(comment_id):
    """Action to delete a comment."""
    if request.form.get('_method') == 'DELETE':
        comment = comments.find_one({'_id': ObjectId(comment_id)})
        comments.delete_one({'_id': ObjectId(comment_id)})
        return redirect(url_for('playlists_show', playlist_id=comment.get('playlist_id')))
    else:
        raise NotFound()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))
