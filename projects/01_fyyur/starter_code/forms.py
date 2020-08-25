from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, TextAreaField
from wtforms.validators import DataRequired, AnyOf, URL, ValidationError
from common import merged, GENRES, STATES, phone_dict


class ShowForm(Form):
    artist_id = StringField(
        'artist_id', validators=[DataRequired()]
    )
    venue_id = StringField(
        'venue_id', validators=[DataRequired()]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )


s = [s.value for s in STATES]


def stateValidator(form, field):
    if field.data not in s:
        raise ValidationError("Invalid State")


g = set([genre.name for genre in GENRES])


def genreValidator(form, field):
    if not set(field.data).issubset(g):
        raise ValidationError("Invalid Genre")


genres = SelectMultipleField(
    'genres', validators=[DataRequired(), genreValidator],
    choices=merged
)


def phoneValidator(form, field):
    # xxx-xxx-xxxx
    # Phone number in USA: (area code 3 digits) (exchange 3 digits ) (number 4 digits)
    # According to: https://www.quora.com/What-is-the-American-mobile-phone-number-format
    possible = phone_dict[form.data.get("state")]

    if len(field.data) != 12 or int(field.data[0:3]) not in possible or field.data[3] != "-" or field.data[7] != "-":
        raise ValidationError("Invalid Phone Number, Must be exactly 12 characters")


state = SelectField(
    'state', validators=[DataRequired(), stateValidator],
    choices=[(s.value, s.value) for s in STATES]
)


def seekingValidator(form, field):
    if field.data not in ['YES', 'NO']:
        raise ValidationError("Invalid choice for Seeking talent")


def seekingDescriptionValidator(form, field):
    isSeeking_1 = form.data.get("seeking_venue")
    isSeeking_2 = form.data.get("seeking_talent")

    if (isSeeking_1 == "YES" or isSeeking_2 == "YES") and len(field.data) == 0:
        raise ValidationError("Cannot leave Seeking Description empty if seeking venue is true")

class VenueForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = state
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone', validators=[DataRequired(), phoneValidator]
    )
    image_link = StringField(
        'image_link'
    )

    genres = genres
    facebook_link = StringField(
        'facebook_link', validators=[DataRequired(), URL()]
    )
    website = StringField(
        'website', validators=[DataRequired(), URL()]
    )
    seeking_talent = SelectField(
        'seeking_talent', validators=[DataRequired(), seekingValidator],
        choices=[
            ('YES', 'YES'),
            ('NO', 'NO')
        ]
    )

    seeking_description = TextAreaField(
        'seeking_description', validators=[seekingDescriptionValidator]
    )



class ArtistForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = state
    phone = StringField(
        'phone', validators=[DataRequired(), phoneValidator]
    )
    image_link = StringField(
        'image_link'
    )

    genres = genres
    facebook_link = StringField(
        'facebook_link', validators=[DataRequired(), URL()]
    )
    website = StringField(
        'website', validators=[DataRequired(), URL()]
    )
    seeking_venue = SelectField(
        'seeking_venue', validators=[DataRequired(), seekingValidator],
        choices=[
            ('YES', 'YES'),
            ('NO', 'NO')
        ]
    )
    seeking_description = TextAreaField(
        'seeking_description', validators=[seekingDescriptionValidator]
    )


class EditArtistForm(Form):
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = state
    phone = StringField(
        'phone', validators=[DataRequired(), phoneValidator]
    )
    image_link = StringField(
        'image_link'
    )

    genres = genres
    facebook_link = StringField(
        'facebook_link', validators=[DataRequired(), URL()]
    )
    website = StringField(
        'website', validators=[DataRequired(), URL()]
    )
    seeking_venue = SelectField(
        'seeking_venue', validators=[DataRequired(), seekingValidator],
        choices=[
            ('YES', 'YES'),
            ('NO', 'NO')
        ]
    )
    seeking_description = TextAreaField(
        'seeking_description', validators=[seekingDescriptionValidator]
    )

class EditVenueForm(Form):
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = state
    phone = StringField(
        'phone', validators=[DataRequired(), phoneValidator]
    )
    image_link = StringField(
        'image_link'
    )

    genres = genres
    facebook_link = StringField(
        'facebook_link', validators=[DataRequired(), URL()]
    )
    website = StringField(
        'website', validators=[DataRequired(), URL()]
    )
    seeking_talent = SelectField(
        'seeking_venue', validators=[DataRequired(), seekingValidator],
        choices=[
            ('YES', 'YES'),
            ('NO', 'NO')
        ]
    )
    seeking_description = TextAreaField(
        'seeking_description', validators=[seekingDescriptionValidator]
    )
