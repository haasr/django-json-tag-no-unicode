"""
Common form fields


These can also be accessed from ``fusionbox.forms``.
"""

import calendar
import datetime
from functools import partial

from django import forms

from fusionbox.forms.widgets import MultiFileWidget


class MonthField(forms.TypedChoiceField):
    """
    :class:`MonthField` is a :class:`TypedChoiceField` that selects a month.
    Its python value is a 1-indexed month number.
    """
    def __init__(self, *args, **kwargs):
        super(MonthField, self).__init__(*args, **kwargs)
        self.choices = [('', ' -- ')] + \
                [(i, "%s - %s" % (i, calendar.month_name[i]))
                        for i in range(1, 13)]
        self.coerce = int

class FutureYearField(forms.TypedChoiceField):
    """
    :class:`FutureYearField` is a :class:`TypedChoiceField` that selects a
    year a defined period in the future. Useful for credit card expiration
    dates.
    """

    def __init__(self, *args, **kwargs):
        number_of_years = kwargs.pop('number_of_years', 6)
        super(FutureYearField, self).__init__(*args, **kwargs)
        self.choices = [('', ' -- ')] + \
                [(i%100, str(i))
                        for i in range(datetime.datetime.now().year, datetime.datetime.now().year + number_of_years)]
        self.coerce = int


class MultiFileField(forms.FileField):
    """
    Implements a multifile field for multiple file uploads.

    This class' `clean` method is implented by currying `super.clean`
    and running map over `data` which is a list of file upload objects received
    from the :class:`MultiFileWidget`.

    Using this field requires a little work on the programmer's part in order
    to use correctly.  Like other Forms with fields that inherit from
    :class:`FileField`, the programmer must pass in the kwarg `files` when creating
    the form instance.  For example:
        ```
        form = MyFormWithFileField(data=request.POST, files=request.FILES)
        ```

    After validation, the cleaned data will be a list of files.  You might
    want to iterate over in a manner similar to this:
        ```
        if form.is_valid():
            for media_file in form.cleaned_data['field_name']:
                MyMedia.objects.create(
                    name=media_file.name,
                    file=media_file
                    )
        ```
    """
    default_error_messages = {
        'required': u'This field is required.',
        'invalid': u'Enter a valid value.',
    }
    widget = MultiFileWidget

    def clean(self, data, initial=None):
        try:
            curry_super = partial(super(MultiFileField, self).clean,
                    initial=initial)
            return map(curry_super, data)
        except TypeError:
            return None
