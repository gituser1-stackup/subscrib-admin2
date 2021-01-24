from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class AlphaNumericValidator:
    def validate(self, password, user=None):
        if not re.findall('\d', password):
            print('Password should have at least one numeral')
            raise ValidationError(
                _("This password must contain at least one Numeric character."),
                code='password_no_numeric',
            )

        if not re.findall('[A-Z]', password):
            print('Password should have at least one uppercase letter')
            raise ValidationError(
                _("This password must contain at least one uppercase character."),
                code='password_no_upper',
            )

        if not re.findall('[a-z]', password):
            print('Password should have at least one lowercase letter')
            raise ValidationError(
                _("This password must contain at least one lowercase letter, a-z."),
                code='password_no_lower',
            )

        if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            print('Password should have at least one of the symbols $@#')
            raise ValidationError(
                _("This password must contain at least one special character:"+
                  "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?"),
                code='password_no_symbol',
            )
        return None

    def get_help_text(self):
        return _(
            "Your password must contain at least one numeral ( 0-9 ), one Uppercase letter( A-z ), one lowercase letter( a-z ) and one special symbol characters( ()[]{}|\`~!@#$%^&*_-+=;:'\",<>./? )."
        )