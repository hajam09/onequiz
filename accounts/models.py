# def getRandomAvatar():
#     return "avatars/" + random.choice(os.listdir(os.path.join(settings.MEDIA_ROOT, "avatars/")))


# class Profile(BaseModel):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
#     url = models.SlugField(max_length=10, editable=settings.DEBUG, unique=True, default=generateString, db_index=True)
#     publicName = models.CharField(max_length=2048, blank=True, null=True)
#     jobTitle = models.CharField(max_length=2048, blank=True, null=True)
#     department = models.CharField(max_length=2048, blank=True, null=True)
#     profilePicture = models.ImageField(upload_to='profile-picture', blank=True, null=True, default=getRandomAvatar)
#
#     class Meta:
#         verbose_name = "Profile"
#         verbose_name_plural = "Profiles"
