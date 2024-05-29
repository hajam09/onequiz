from django import template
from django.core.paginator import Page
from django.forms.widgets import (
    CheckboxInput,
    CheckboxSelectMultiple,
    ClearableFileInput,
    NumberInput,
    RadioSelect,
    Select,
    TextInput,
    Textarea
)
from django.urls import reverse
from django.utils.safestring import mark_safe

from onequiz.base.utils.navigationBar import linkItem, Icon

register = template.Library()


@register.simple_tag
def navigationPanel(request):
    links = [
        linkItem('Home', reverse('core:index-view'), None),
    ]

    if request.user.is_authenticated:
        links.extend(
            [
                linkItem('Create a Quiz', reverse('core:quiz-create-view'), None),
                linkItem('Account', '', None, [
                    linkItem('History', reverse('core:attempted-quizzes-view'), Icon('', 'fas fa-book-open', '15')),
                    linkItem('My Quizzes', reverse('core:user-created-quizzes-view'),
                             Icon('', 'fas fa-question', '15')),
                    None,
                    linkItem('Logout', reverse('accounts:logout'), Icon('', 'fas fa-sign-out-alt', '15')),
                ]),
            ]
        )
    else:
        links.append(
            linkItem('Login / Register', '', None, [
                linkItem('Register', reverse('accounts:register'), Icon('', 'fas fa-user-circle', '20')),
                None,
                linkItem('Login', reverse('accounts:login'), Icon('', 'fas fa-sign-in-alt', '20')),
            ]),
        )
    return links


@register.simple_tag
def paginationComponent(request, objects: Page):
    if not objects.has_other_pages():
        return mark_safe('<span></span>')

    query = f"&query={request.GET.get('query')}" if request.GET.get('query') else ''

    if objects.has_previous():
        href = f'?page={objects.previous_page_number()}{query}'
        previousPageLink = f'''
        <li class="page-item">
            <a class="page-link" href="{href}" tabindex="-1">Previous</a>
        </li>
        '''
        firstPageLink = f'''
        <li class="page-item">
            <a class="page-link" href="?page=1{query}" tabindex="-1">First</a>
        </li>
        '''

    else:
        previousPageLink = f'''
        <li class="page-item disabled">
            <a class="page-link" href="#" tabindex="-1">Previous</a>
        </li>
        '''
        firstPageLink = f'''
        <li class="page-item disabled">
            <a class="page-link" href="?page=1{query}" tabindex="-1">First</a>
        </li>
        '''

    if objects.has_next():
        href = f'?page={objects.next_page_number()}{query}'
        nextPageLink = f'''
        <li class="page-item">
            <a class="page-link" href="{href}" tabindex="-1">Next</a>
        </li>
        '''
        lastPageLink = f'''
        <li class="page-item">
            <a class="page-link" href="?page={objects.paginator.num_pages}{query}" tabindex="-1">Last</a>
        </li>
        '''

    else:
        nextPageLink = f'''
        <li class="page-item disabled">
            <a class="page-link" href="#" tabindex="-1">Next</a>
        </li>
        '''
        lastPageLink = f'''
        <li class="page-item disabled">
            <a class="page-link" href="?page={objects.paginator.num_pages}{query}" tabindex="-1">Last</a>
        </li>
        '''

    pageNumberLinks = ''
    EITHER_SIDE_PAGE_LIMIT = 20
    pageRange = objects.paginator.page_range
    if pageRange.stop > EITHER_SIDE_PAGE_LIMIT:
        currentPage = int(request.GET.get('page') or 1)
        minRange = currentPage - EITHER_SIDE_PAGE_LIMIT // 2
        maxRange = currentPage + EITHER_SIDE_PAGE_LIMIT // 2

        if minRange <= 0:
            minRange = 1
        if maxRange > pageRange.stop:
            maxRange = pageRange.stop

        pageRange = range(minRange, maxRange)

    for pageNumber in pageRange:
        if objects.number == pageNumber:
            pageNumberLinks += f'''
                <li class="page-item active"><a class="page-link" href="#">{pageNumber}</a></li>
            '''
        else:
            href = f"?page={pageNumber}{query}"
            pageNumberLinks += f'''
                <li class="page-item"><a class="page-link" href="{href}">{pageNumber}</a></li>
            '''

    itemContent = f'''
    <div class="row">
        <div class="col-md-12" style="width: 1100px;">
            <nav aria-label="Page navigation example">
                <ul class="pagination justify-content-center">
                    {firstPageLink}
                    {previousPageLink}
                    {pageNumberLinks}
                    {nextPageLink}
                    {lastPageLink}
                </ul>
            </nav>
        </div>
    </div>
    '''
    return mark_safe(itemContent)


@register.simple_tag
def renderFormFields(field):
    body = ''
    if (isinstance(field.field.widget, ClearableFileInput) or isinstance(field.field.widget, NumberInput)
            or isinstance(field.field.widget, Select) or isinstance(field.field.widget, TextInput)
            or isinstance(field.field.widget, Textarea)):
        label = f'<span class="form-label">{field.label}</span>'
        body = str(field)
    elif isinstance(field.field.widget, CheckboxInput):
        label = f'<span class="form-label"></span>'
        for checkbox in field.subwidgets:
            body += f'''
                <div class="row">
                    <div class="col-auto">
                        <div class="multiple-choice">
                            <input type={checkbox.data.get('type')} name={checkbox.data.get('name')}
                            id={checkbox.data.get('attrs').get('id')} class={checkbox.data.get('attrs').get('class')}
                            style="height: 34px; width: 34px;" {"required" if checkbox.data.get('selected') else ""}
                            {"checked" if checkbox.data.get('attrs').get('checked') else ""}>
                        </div>
                    </div>
                    <div class="col">
                        <label class="form-label" style="padding-top: 5px">{field.label}</label>
                    </div>
                </div>'''
    elif isinstance(field.field.widget, CheckboxSelectMultiple):
        label = f'<h5 class="form-label">{field.label}</h5>'
        for checkbox in field.subwidgets:
            body += f'''
                <div class="row">
                    <div class="col-auto">
                        <input type={checkbox.data.get('type')} name={checkbox.data.get('name')}
                                value={checkbox.data.get('value')} style="{checkbox.data.get('attrs').get('style')}"
                                id={checkbox.data.get('attrs').get('id')} {checkbox.data.get('attrs').get('disabled')}
                                {"checked" if checkbox.data.get('selected') else ""}>
                    </div>
                    <div class="col">
                    <input type="text" class="form-control col" disabled="" value="{checkbox.data.get('label')}">
                </div>
            </div>'''
    elif isinstance(field.field.widget, RadioSelect):
        label = f'<h5 class="form-label">{field.label}</h5>'
        for radio in field.subwidgets:
            body += f'''
                <div class="form-check form-check-inline">
                    <input type={radio.data.get('type')} name={radio.data.get('name')} value={radio.data.get('value')}
                    class={radio.data.get('attrs').get('class')} style="{radio.data.get('attrs').get('style')}"
                    {"required" if radio.data.get('attrs').get('required') else ""}
                    {radio.data.get('attrs').get('disabled')}
                    id={radio.data.get('attrs').get('id')} {"checked" if radio.data.get('selected') else ""}>
                    <label class="form-check-label" for={radio.data.get('attrs').get('id')}>{radio.choice_label}</label>
                </div>'''
    else:
        raise Exception(f'Unsupported field type: {field.field.widget.__class__}')
    return mark_safe(label + body)
