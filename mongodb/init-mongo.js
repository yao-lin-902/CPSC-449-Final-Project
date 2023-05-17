db.createUser({
  user: 'root',
  pwd: 'root',
  roles: [
    {
      role: 'readWrite',
      db: 'library',
    },
  ],
})

db = new Mongo().getDB('library')

db.createCollection('books')
