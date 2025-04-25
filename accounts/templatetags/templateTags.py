from django import template
from django.core.paginator import Page
from django.forms.widgets import (
    CheckboxInput,
    CheckboxSelectMultiple,
    ClearableFileInput,
    HiddenInput,
    NumberInput,
    RadioSelect,
    Select,
    TextInput,
    Textarea
)
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.models import QuizAttempt, Question
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
                        <small><b>{field.help_text}</b></small>
                    </div>
                </div>'''
    elif isinstance(field.field.widget, CheckboxSelectMultiple) or isinstance(field.field.widget, RadioSelect):
        label = f'<h5 class="form-label">{field.label}</h5>'
        for widget in field.subwidgets:
            body += f'''
                <div class="row">
                    <div class="col-auto">
                        <input type={widget.data.get('type')} name={widget.data.get('name')}
                                value={widget.data.get('value')} style="{widget.data.get('attrs').get('style')}"
                                id={widget.data.get('attrs').get('id')} {widget.data.get('attrs').get('disabled')}
                                {"checked" if widget.data.get('selected') else ""}>
                    </div>
                    <div class="col">
                    <input type="text" class="form-control col" disabled="" value="{widget.data.get('label')}">
                </div>
            </div>'''
    elif isinstance(field.field.widget, HiddenInput):
        label = ''
        body = str(field)
    else:
        raise Exception(f'Unsupported field type: {field.field.widget.__class__}')
    return mark_safe(label + body)


@register.simple_tag
def renderScoreComponent(user, quizAttempt, form):
    canMark = quizAttempt.getPermissionMode(user) == QuizAttempt.Mode.MARK
    isMarked = quizAttempt.getPermissionMode(user) == QuizAttempt.Mode.VIEW and quizAttempt.status == QuizAttempt.Status.MARKED

    if form.response.question.questionType == Question.Type.ESSAY:
        name = f"awarded-mark-for-essay-{form.response.id}"
    elif form.response.question.questionType == Question.Type.TRUE_OR_FALSE:
        name = f"awarded-mark-for-true-or-false-{form.response.id}"
    elif form.response.question.questionType == Question.Type.MULTIPLE_CHOICE:
        name = f"awarded-mark-for-mcq-{form.response.id}"
    else:
        raise Exception(f"Unsupported response type: {form.response.question}")

    if form.data.get('markResponseAlert') == 'border border-success':
        awardedMark = int(form.response.mark)
    elif form.data.get('markResponseAlert') == 'border border-secondary':
        awardedMark = '' if form.response.mark is None else int(form.response.mark)
    else:
        awardedMark = ''

    if canMark or isMarked:
        itemContent = f'''
        <span>
            <div class="row">
                <div class="col">
                    <div class="text-right">
                        <div class="row float-right">
                            <div class="col-auto">
                                <input type="number" class="form-control" value="{awardedMark}" name="{name}"
                                {"disabled" if quizAttempt.user == user else ""}
                                min="0" max="{form.response.question.mark}"
                                style="width: 40px; padding-left: 10px;padding-right: 10px;">
                            </div>
                            <b style="font-size: 26px;">/</b>
                            <div class="col-auto">
                                <input disabled type="number" class="form-control"
                                value="{form.response.question.mark}"
                                style="width: 40px; padding-left: 10px; padding-right: 10px;">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <br>
            </span>
        '''
    else:
        itemContent = '''<span></span>'''
    return mark_safe(itemContent)


@register.filter
def startswith(value, arg):
    return value.startswith(arg)
