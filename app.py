from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.exceptions import NotFound
import os

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/Playlister')
client = MongoClient(host=f'{host}?retryWrites=false')
db = client.get_default_database()

playlists = db.playlists
comments = db.comments

app = Flask(__name__)


@app.route('/')
def playlists_index():
    """Show all playlists."""
    playlist = playlists.find()
    # This will display all playlists by looping through the database
    return render_template('playlists_index.html', playlist=playlist)


@app.route('/playlists', methods=['POST'])
def playlists_submit():
    """Submit a new playlist."""
    playlist = {
        'title': request.form.get('title'),
        'description': request.form.get('description'),
        'videos': request.form.get('videos').split(),
        'created_at': datetime.now()
    }
    print(playlist)
    playlist_id = playlists.insert_one(playlist).inserted_id
    return redirect(url_for('playlists_show', playlist_id=playlist_id))


@app.route('/playlists/new')
def playlists_new():
    """Create a new playlist."""
    # This route will create a new playlist and display the playist_form.html
    return render_template('playlists_new.html', playlist={}, title='New Playlist')


@app.route('/playlists/<id>/edit')
def playlists_edit(playlist_id):
    """Show the edit form for a playlist."""
    # This will edit a specific playlist by its id
    playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
    video_links = '\n'.join(playlist.get('videos'))
    return render_template('playlists_edit.html', playlist=playlist)


@app.route('/playlists/<playlist_id>')
def playlists_show(playlist_id):
    """Show a single playlist."""
    playlist = playlists.find_one({'_id': ObjectId(playlist_id)})
    playlist_comments = comments.find({'playlist_id': ObjectId(playlist_id)})
    return render_template('playlists_show.html', playlist=playlist, comments=playlist_comments)


@app.route('/playlists/<playlist_id>', methods=['POST'])
# This will call on either to display or edit a playlist based on what the user submits
def playlists_update(playlist_id):
    """Submit an edited playlist."""
    if request.form.get('_method') == 'PUT':
        updated_playlist = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'videos': request.form.get('videos').split()
        }
        playlists.update_one(
            {'_id': ObjectId(playlist_id)},
            {'$set': updated_playlist})
        return redirect(url_for('playlists_show', playlist_id=playlist_id))
    else:
        raise NotFound()


@app.route('/playlists/<playlist_id>/delete', methods=['POST'])
def playlists_delete(playlist_id):
    # This will delete a playlist by using an id as a parameter
    """Delete one playlist."""
    if request.form.get('_method') == 'DELETE':
        playlists.delete_one({'_id': ObjectId(playlist_id)})
        return redirect(url_for('playlists_index'))
    else:
        raise NotFound()


@app.route('/playlists/comments', methods=['POST'])
def comments_new():
    """Submit a new comment."""
    comment = {
        'title': request.form.get('title'),
        'content': request.form.get('content'),
        'playlist_id': ObjectId(request.form.get('playlist_id'))
    }
    print(comment)
    comment_id = comments.insert_one(comment).inserted_id
    return redirect(url_for('playlists_show', comment_id=comment_id))


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
