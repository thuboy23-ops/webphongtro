from django import forms

from .models import Phong, UserProfile


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(item, initial) for item in data]
        if not data:
            return []
        return [single_file_clean(data, initial)]


ROLE_CHOICES_ALL = [
    (UserProfile.Role.TENANT, "Khách thuê"),
    (UserProfile.Role.LANDLORD, "Chủ trọ"),
    (UserProfile.Role.ADMIN, "Quản trị viên hệ thống"),
]

ROLE_CHOICES_REGISTER = [
    (UserProfile.Role.TENANT, "Khách thuê"),
    (UserProfile.Role.LANDLORD, "Chủ trọ"),
]


class LoginForm(forms.Form):
    identifier = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES_ALL)


class RegisterForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES_REGISTER)


class RoomForm(forms.ModelForm):
    ROOM_TYPE_CHOICES = [
        ("", "Chọn loại phòng"),
        ("Phòng thường", "Phòng thường"),
        ("Phòng điều hòa", "Phòng điều hòa"),
        ("Phòng nóng lạnh", "Phòng nóng lạnh"),
        ("Phòng đầy đủ", "Phòng đầy đủ"),
    ]
    KHU_VUC_CHOICES = [
        ("", "Chọn khu vực"),
        ("Gần Đại học Sư phạm Thái Nguyên", "Gần Đại học Sư phạm Thái Nguyên"),
        ("Gần Đại học Kỹ thuật Công nghiệp", "Gần Đại học Kỹ thuật Công nghiệp"),
        ("Gần Đại học Công nghệ Thông tin và Truyền thông", "Gần Đại học Công nghệ Thông tin và Truyền thông"),
        ("Gần Đại học Nông Lâm Thái Nguyên", "Gần Đại học Nông Lâm Thái Nguyên"),
        ("Gần Đại học Khoa học Thái Nguyên", "Gần Đại học Khoa học Thái Nguyên"),
        ("Gần Đại học Y - Dược Thái Nguyên", "Gần Đại học Y - Dược Thái Nguyên"),
        ("Khu Đại học Thái Nguyên (Tân Thịnh)", "Khu Đại học Thái Nguyên (Tân Thịnh)"),
    ]
    STATUS_CHOICES = [
        ("available", "Còn trống"),
        ("rented", "Đang thuê"),
        ("maintenance", "Đang sửa chữa"),
    ]

    khu_vuc = forms.ChoiceField(choices=KHU_VUC_CHOICES, required=False)
    gallery_images = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={"multiple": True}),
    )

    class Meta:
        model = Phong
        fields = [
            "title",
            "price",
            "area",
            "address",
            "latitude",
            "longitude",
            "room_type",
            "status",
            "description",
            "owner_phone",
            "image",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_class = "mt-1 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none ring-indigo-500 focus:ring"
        self.fields["room_type"].widget = forms.Select(choices=self.ROOM_TYPE_CHOICES)
        self.fields["status"].widget = forms.Select(choices=self.STATUS_CHOICES)
        self.fields["price"].widget = forms.TextInput()
        self.fields["latitude"].widget = forms.HiddenInput(attrs={"id": "id_latitude"})
        self.fields["longitude"].widget = forms.HiddenInput(attrs={"id": "id_longitude"})
        for name, field in self.fields.items():
            if name == "description":
                field.widget.attrs.update({"class": base_class, "rows": 5})
            elif name == "price":
                field.widget.attrs.update(
                    {
                        "class": base_class,
                        "inputmode": "numeric",
                        "placeholder": "Ví dụ: 1,000,000",
                        "data-format-price": "true",
                    }
                )
            else:
                field.widget.attrs.update({"class": base_class})

        self.fields["image"].widget.attrs.update({"accept": "image/*"})
        self.fields["gallery_images"].widget.attrs.update(
            {
                "class": base_class,
                "accept": "image/*",
            }
        )

    def clean(self):
        cleaned_data = super().clean()
        address = cleaned_data.get("address", "").strip()
        khu_vuc = cleaned_data.get("khu_vuc", "").strip()
        if khu_vuc and khu_vuc.lower() not in address.lower():
            cleaned_data["address"] = f"{address}, {khu_vuc}" if address else khu_vuc
        return cleaned_data
