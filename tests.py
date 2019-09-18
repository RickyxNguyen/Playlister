from unittest import TestCase, main as unittest_main, mock
from bson.objectid import ObjectId
from app import app

sample_playlist_id = ObjectId('5d55cffc4a3d4031f42827a3')
sample_playlist = {
    'title': 'Cat Videos',
    'description': 'Cats acting weird',
    'videos': [
        'https://youtube.com/embed/hY7m5jjJ9mM',
        'https://www.youtube.com/embed/CQ85sUNBK7w'
    ]
}


@mock.patch('pymongo.collection.Collection.find_one')
class PlaylistsTests(TestCase):
    """Flask tests."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

    def test_index(self):
        """Test the playlists homepage."""
        result = self.client.get('/')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'Playlists', result.data)

    def test_new(self):
        """Test the new playlist creation page."""
        result = self.client.get('/playlists/new')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'New Playlist', result.data)

    def test_show_playlist(self, mock_find):
        """Test showing a single playlist."""
        mock_find.return_value = sample_playlist
        result = self.client.get(f'/playlists/{sample_playlist_id}')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'La La Land', result.data)

    def test_edit_playlist(self, mock_find):
        """Test editing a single playlist."""
        mock_find.return_value = sample_playlist

        result = self.client.get(f'/playlists/{sample_playlist_id}/edit')
        self.assertEqual(result.status, '200 OK')
        self.assertIn(b'La La Land', result.data)

    def test_submit_playlist(self, mock_insert):
        """Test submitting a new playlist."""
        result = self.client.post('/playlists', data=sample_playlist)

        # After submitting, should redirect to that playlist's page
        self.assertEqual(result.status, '302 FOUND')
        mock_insert.assert_called_with(sample_playlist)

    def test_update_playlist(self, mock_update):
        form_data = {'_method': 'PUT', **sample_playlist}
        result = self.client.post(
            f'/playlists/{sample_playlist_id}', data=form_data)
        self.assertEqual(result.status, '302 FOUND')
        mock_update.assert_called_with({'_id': sample_playlist_id}, {
                                       '$set': sample_playlist})

    def test_delete_playlist(self, mock_delete):
        form_data = {'_method': 'DELETE'}
        mock_find.return_value = sample_playlist

        result = self.client.post(
            f'/playlists/{sample_playlist_id}/delete', data=form_data)
        self.assertEqual(result.status, '302 FOUND')
        mock_delete.assert_called_with({'_id': sample_playlist_id})


if __name__ == '__main__':
    unittest_main()
