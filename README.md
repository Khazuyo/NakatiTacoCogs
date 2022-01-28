# Nakati Taco Cogs

Various cogs for RED Discord Bot v3.

I'm releasing those under the terms of the GNU AGPL license (see the LICENSE file) so please make sure you agree to its terms before re-using anything, thanks! (:

## What's inside?

This project contains the following cogs:

### `avaliimages`

The Avali Images cog displays a random (Avali) image. In theory this should work with any picture upload.
Users can post their submissions one by one, providing some text in a specific format:

```
Title: <Image Title>
Artist: <Name of the Artist(s)>
Source: <URL to source or artist's gallery>
```

This allows the bot to post some information about the origin of the image so people can find the artist easier.
I added this because I was getting tired of images being posted but nobody could tell who drew them etc.

In your image channel in Discord you must then use the `chirpset syncdb` to instruct the bot to parse all the image uploads and add them to its database.
If there's a mistake in the submission's message the bot will notify the poster(s).

### `cute`

The `cute` cog picks a random user from the current chat's last n entries and declares them the "Cutie of the next xx Minutes".
If `cute` is used within the timespan of xx Minutes it will simply repeat who's the current Cutie.
